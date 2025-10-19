from typing import Dict, Any, List
import requests
import time
from . import BaseAgent


class ProspectSearchAgent(BaseAgent):
    """
    Agent responsible for searching and finding prospects
    Uses Apollo API (or mock data if API unavailable)
    """
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for prospects matching ICP criteria
        
        Args:
            inputs: Contains ICP criteria and search parameters
            
        Returns:
            Dictionary with 'leads' array
        """
        self.think("Starting prospect search based on ICP criteria")
        
        icp = inputs.get('icp', {})
        signals = inputs.get('signals', [])
        limit = inputs.get('limit', 10)
        
        self.think(f"ICP: {icp.get('industry')} companies in {icp.get('location')} "
                  f"with {icp['employee_count']['min']}-{icp['employee_count']['max']} employees")
        
        # Try Apollo API first
        leads = self._search_apollo_api(icp, signals, limit)
        
        # If API fails, use mock data
        if not leads:
            self.observe("Apollo API unavailable, using mock data for demonstration")
            leads = self._generate_mock_leads(icp, limit)
        
        self.observe(f"Found {len(leads)} qualified leads")
        
        output = {'leads': leads}
        self.validate_output(output)
        
        return output
    
    def _search_apollo_api(self, icp: Dict, signals: List[str], limit: int) -> List[Dict]:
        """Search using Apollo API"""
        if 'ApolloAPI' not in self.tools_config:
            return []
        
        api_config = self.tools_config['ApolloAPI']
        api_key = api_config.get('api_key')
        
        if not api_key or api_key == '':
            self.observe("Apollo API key not configured")
            return []
        
        self.act("Calling Apollo API", {'endpoint': 'mixed_people/search'})
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache',
                'X-Api-Key': api_key
            }
            
            payload = {
                "person_titles": ["VP", "Director", "Head", "Chief", "Manager"],
                "person_seniorities": ["vp", "director", "head"],
                "organization_locations": [icp.get('location', 'USA')],
                "organization_num_employees_ranges": [
                    f"{icp['employee_count']['min']},{icp['employee_count']['max']}"
                ],
                "page": 1,
                "per_page": min(limit, 25)
            }
            
            response = requests.post(
                api_config.get('endpoint', 'https://api.apollo.io/v1/mixed_people/search'),
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                people = data.get('people', [])
                
                leads = []
                for person in people[:limit]:
                    lead = {
                        'company': person.get('organization', {}).get('name', 'Unknown'),
                        'contact_name': person.get('name', 'Unknown'),
                        'email': person.get('email', ''),
                        'title': person.get('title', ''),
                        'linkedin': person.get('linkedin_url', ''),
                        'company_size': person.get('organization', {}).get('estimated_num_employees', 0),
                        'signal': signals[0] if signals else 'general_outreach'
                    }
                    leads.append(lead)
                
                self.observe(f"Apollo API returned {len(leads)} leads")
                return leads
            else:
                self.observe(f"Apollo API error: {response.status_code}")
                return []
                
        except Exception as e:
            self.observe(f"Apollo API exception: {str(e)}")
            return []
    
    def _generate_mock_leads(self, icp: Dict, limit: int) -> List[Dict]:
        """Generate mock leads for demonstration"""
        mock_companies = [
            ("Salesforce", "Sarah Johnson", "sarah.johnson@salesforce.com", "VP of Sales", 500),
            ("HubSpot", "Michael Chen", "m.chen@hubspot.com", "Director of Marketing", 450),
            ("Zendesk", "Emily Rodriguez", "emily.r@zendesk.com", "Head of Business Development", 380),
            ("Atlassian", "David Park", "david.park@atlassian.com", "VP of Enterprise Sales", 600),
            ("Shopify", "Amanda Williams", "a.williams@shopify.com", "Director of Partnerships", 420),
            ("Slack", "James Martinez", "james.m@slack.com", "Head of Sales Operations", 350),
            ("Zoom", "Lisa Thompson", "l.thompson@zoom.us", "VP of Customer Success", 550),
            ("DocuSign", "Robert Garcia", "r.garcia@docusign.com", "Director of Sales", 400),
            ("Twilio", "Jessica Lee", "jessica.lee@twilio.com", "Head of Growth", 380),
            ("Stripe", "Christopher Brown", "chris.brown@stripe.com", "VP of Business Development", 500)
        ]
        
        leads = []
        for i, (company, name, email, title, size) in enumerate(mock_companies[:limit]):
            signal = icp.get('signals', ['general_outreach'])[i % len(icp.get('signals', ['general_outreach']))]
            
            lead = {
                'company': company,
                'contact_name': name,
                'email': email,
                'title': title,
                'linkedin': f"https://linkedin.com/in/{name.lower().replace(' ', '-')}",
                'company_size': size,
                'signal': signal if isinstance(signal, str) else 'general_outreach'
            }
            leads.append(lead)
        
        return leads