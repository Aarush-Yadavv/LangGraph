from typing import Dict, Any, List
from . import BaseAgent


class ScoringAgent(BaseAgent):
    """
    Agent responsible for scoring and ranking leads based on ICP criteria
    """
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score and rank leads based on ICP match
        
        Args:
            inputs: Contains 'enriched_leads' and 'scoring_criteria'
            
        Returns:
            Dictionary with 'ranked_leads' array (sorted by score)
        """
        self.think("Starting lead scoring based on ICP criteria")
        
        enriched_leads = inputs.get('enriched_leads', [])
        scoring_criteria = inputs.get('scoring_criteria', {})
        
        self.think(f"Scoring {len(enriched_leads)} leads using weighted criteria")
        
        # Get scoring weights
        weights = scoring_criteria.get('weights', {
            'revenue_match': 0.3,
            'employee_match': 0.2,
            'technology_match': 0.2,
            'signal_strength': 0.3
        })
        
        # Get minimum score threshold
        min_score = scoring_criteria.get('thresholds', {}).get('min_score', 60)
        
        ranked_leads = []
        
        for lead in enriched_leads:
            self.act(f"Scoring lead: {lead.get('company')}")
            
            # Calculate individual scores
            score_breakdown = self._calculate_score_breakdown(lead, weights)
            
            # Calculate total score
            total_score = sum(score_breakdown.values())
            
            # Only include leads above threshold
            if total_score >= min_score:
                ranked_lead = {
                    'company': lead.get('company'),
                    'contact': lead.get('contact'),
                    'email': lead.get('email'),
                    'role': lead.get('role'),
                    'score': round(total_score, 2),
                    'score_breakdown': score_breakdown,
                    'technologies': lead.get('technologies', []),
                    'company_description': lead.get('company_description', ''),
                    'recent_news': lead.get('recent_news', '')
                }
                ranked_leads.append(ranked_lead)
                
                self.observe(f"{lead.get('company')} scored {total_score:.2f}")
        
        # Sort by score (highest first)
        ranked_leads.sort(key=lambda x: x['score'], reverse=True)
        
        self.observe(f"Ranked {len(ranked_leads)} leads above threshold ({min_score})")
        
        output = {'ranked_leads': ranked_leads}
        self.validate_output(output)
        
        return output
    
    def _calculate_score_breakdown(self, lead: Dict, weights: Dict) -> Dict[str, float]:
        """
        Calculate individual score components
        
        Args:
            lead: Lead data
            weights: Scoring weights
            
        Returns:
            Dictionary with score breakdown
        """
        breakdown = {}
        
        # Revenue match score (0-100)
        # Assuming leads are pre-filtered, give high score
        revenue_score = 90  # Mock: In real system, compare against actual revenue
        breakdown['revenue_match'] = revenue_score * weights.get('revenue_match', 0.3)
        
        # Employee match score (0-100)
        # Based on company size in ICP range
        employee_score = 85
        breakdown['employee_match'] = employee_score * weights.get('employee_match', 0.2)
        
        # Technology match score (0-100)
        # Score based on relevant technologies used
        tech_score = self._score_technologies(lead.get('technologies', []))
        breakdown['technology_match'] = tech_score * weights.get('technology_match', 0.2)
        
        # Signal strength score (0-100)
        # Based on recent activity/news
        signal_score = self._score_signals(lead)
        breakdown['signal_strength'] = signal_score * weights.get('signal_strength', 0.3)
        
        return breakdown
    
    def _score_technologies(self, technologies: List[str]) -> float:
        """
        Score based on technology stack
        
        Args:
            technologies: List of technologies used
            
        Returns:
            Score 0-100
        """
        # High-value technologies that indicate good fit
        valuable_tech = {
            'Salesforce': 20,
            'HubSpot': 20,
            'AWS': 15,
            'Azure': 15,
            'Google Cloud': 15,
            'Slack': 10,
            'Zoom': 10,
            'Docker': 10,
            'Kubernetes': 10
        }
        
        score = 0
        for tech in technologies:
            score += valuable_tech.get(tech, 5)  # Default 5 points for any tech
        
        # Cap at 100
        return min(score, 100)
    
    def _score_signals(self, lead: Dict) -> float:
        """
        Score based on buying signals
        
        Args:
            lead: Lead data
            
        Returns:
            Score 0-100
        """
        score = 50  # Base score
        
        recent_news = lead.get('recent_news', '').lower()
        
        # Positive signals
        if 'funding' in recent_news or 'raised' in recent_news:
            score += 30
        if 'hiring' in recent_news or 'expands' in recent_news:
            score += 20
        if 'growth' in recent_news or 'earnings' in recent_news:
            score += 15
        if 'new product' in recent_news or 'launches' in recent_news:
            score += 10
        
        # VP/Director level contacts get bonus
        role = lead.get('role', '').lower()
        if 'vp' in role or 'vice president' in role:
            score += 10
        elif 'director' in role:
            score += 5
        
        return min(score, 100)