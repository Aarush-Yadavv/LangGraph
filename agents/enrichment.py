from typing import Dict, Any, List
import requests
from . import BaseAgent


class DataEnrichmentAgent(BaseAgent):
    """
    Agent responsible for enriching lead data with additional information
    Uses Clearbit API (or mock enrichment if API unavailable)
    """
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich leads with additional company and contact data
        
        Args:
            inputs: Contains 'leads' from previous step
            
        Returns:
            Dictionary with 'enriched_leads' array
        """
        self.think("Starting data enrichment for leads")
        
        leads = inputs.get('leads', [])
        self.think(f"Enriching {len(leads)} leads")
        
        enriched_leads = []
        
        for lead in leads:
            self.act(f"Enriching data for {lead.get('company')}")
            
            # Try Clearbit API
            enriched_data = self._enrich_with_clearbit(lead)
            
            # If API fails, use mock enrichment
            if not enriched_data:
                enriched_data = self._mock_enrich_lead(lead)
            
            enriched_leads.append(enriched_data)
        
        self.observe(f"Successfully enriched {len(enriched_leads)} leads")
        
        output = {'enriched_leads': enriched_leads}
        self.validate_output(output)
        
        return output
    
    def _enrich_with_clearbit(self, lead: Dict) -> Dict:
        """Enrich using Clearbit API"""
        if 'Clearbit' not in self.tools_config:
            return None
        
        api_config = self.tools_config['Clearbit']
        api_key = api_config.get('api_key')
        
        if not api_key or api_key == '':
            return None
        
        try:
            # Clearbit Enrichment API
            company_domain = lead.get('email', '').split('@')[-1]
            
            headers = {
                'Authorization': f'Bearer {api_key}'
            }
            
            # Company enrichment
            response = requests.get(
                f'https://company.clearbit.com/v2/companies/find?domain={company_domain}',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                enriched = {
                    'company': lead.get('company'),
                    'contact': lead.get('contact_name'),
                    'email': lead.get('email'),
                    'role': lead.get('title'),
                    'technologies': data.get('tech', []),
                    'company_description': data.get('description', ''),
                    'recent_news': self._fetch_recent_news(lead.get('company'))
                }
                
                self.observe(f"Clearbit enrichment successful for {lead.get('company')}")
                return enriched
            else:
                return None
                
        except Exception as e:
            self.observe(f"Clearbit API error: {str(e)}")
            return None
    
    def _mock_enrich_lead(self, lead: Dict) -> Dict:
        """Generate mock enrichment data"""
        
        # Mock technology stacks by company type
        tech_stacks = {
            'default': ['Salesforce', 'HubSpot', 'Slack', 'Google Workspace'],
            'saas': ['AWS', 'React', 'PostgreSQL', 'Redis', 'Docker'],
            'enterprise': ['Microsoft Azure', 'SAP', 'Oracle', 'Tableau']
        }
        
        # Mock recent news
        news_templates = [
            f"{lead.get('company')} announces Q4 growth of 25%",
            f"{lead.get('company')} expands sales team with 15 new hires",
            f"{lead.get('company')} raises Series B funding",
            f"{lead.get('company')} launches new product line",
            f"{lead.get('company')} opens new office in San Francisco"
        ]
        
        import random
        
        enriched = {
            'company': lead.get('company'),
            'contact': lead.get('contact_name'),
            'email': lead.get('email'),
            'role': lead.get('title'),
            'technologies': tech_stacks['saas'] if 'VP' in lead.get('title', '') else tech_stacks['default'],
            'company_description': f"{lead.get('company')} is a leading technology company specializing in enterprise software solutions. They serve mid-market and enterprise customers across North America.",
            'recent_news': random.choice(news_templates)
        }
        
        return enriched
    
    def _fetch_recent_news(self, company_name: str) -> str:
        """Fetch recent news about company (mock implementation)"""
        news_items = [
            f"{company_name} reports strong quarterly earnings",
            f"{company_name} expands into new markets",
            f"{company_name} announces strategic partnership",
            f"{company_name} releases innovative product update"
        ]
        
        import random
        return random.choice(news_items)