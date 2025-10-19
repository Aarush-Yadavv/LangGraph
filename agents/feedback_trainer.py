from typing import Dict, Any, List
from datetime import datetime
import json
from . import BaseAgent


class FeedbackTrainerAgent(BaseAgent):
    """
    Agent responsible for analyzing campaign performance and generating recommendations
    Uses Google Sheets for storing feedback and recommendations
    """
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze campaign performance and generate improvement recommendations
        
        Args:
            inputs: Contains 'responses', 'messages', and 'scored_leads'
            
        Returns:
            Dictionary with 'metrics' and 'recommendations'
        """
        self.think("Starting campaign performance analysis")
        
        responses = inputs.get('responses', [])
        messages = inputs.get('messages', [])
        scored_leads = inputs.get('scored_leads', [])
        
        self.think(f"Analyzing {len(responses)} campaign responses")
        
        # Calculate metrics
        metrics = self._calculate_metrics(responses)
        
        self.observe(f"Metrics calculated: Open rate: {metrics['open_rate']:.1f}%, "
                    f"Reply rate: {metrics['reply_rate']:.1f}%")
        
        # Generate recommendations based on performance
        recommendations = self._generate_recommendations(metrics, messages, scored_leads)
        
        self.observe(f"Generated {len(recommendations)} recommendations")
        
        # Save to Google Sheets
        self._save_to_sheets(metrics, recommendations)
        
        output = {
            'metrics': metrics,
            'recommendations': recommendations
        }
        
        self.validate_output(output)
        
        return output
    
    def _calculate_metrics(self, responses: List[Dict]) -> Dict[str, float]:
        """
        Calculate campaign performance metrics
        
        Args:
            responses: List of email engagement data
            
        Returns:
            Dictionary with calculated metrics
        """
        total = len(responses)
        
        if total == 0:
            return {
                'open_rate': 0,
                'click_rate': 0,
                'reply_rate': 0,
                'meeting_rate': 0
            }
        
        opened = sum(1 for r in responses if r.get('opened', False))
        clicked = sum(1 for r in responses if r.get('clicked', False))
        replied = sum(1 for r in responses if r.get('replied', False))
        meetings = sum(1 for r in responses if r.get('meeting_booked', False))
        
        metrics = {
            'total_sent': total,
            'total_opened': opened,
            'total_clicked': clicked,
            'total_replied': replied,
            'total_meetings': meetings,
            'open_rate': (opened / total * 100) if total > 0 else 0,
            'click_rate': (clicked / total * 100) if total > 0 else 0,
            'reply_rate': (replied / total * 100) if total > 0 else 0,
            'meeting_rate': (meetings / total * 100) if total > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        return metrics
    
    def _generate_recommendations(self, metrics: Dict, messages: List[Dict], 
                                  scored_leads: List[Dict]) -> List[Dict]:
        """
        Generate actionable recommendations based on performance
        
        Args:
            metrics: Campaign metrics
            messages: Email messages sent
            scored_leads: Scored lead data
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Analyze open rate
        if metrics['open_rate'] < 20:
            recommendations.append({
                'category': 'Subject Lines',
                'suggestion': 'Open rate is below industry average (20%). Consider testing more personalized subject lines that reference company-specific news or pain points.',
                'confidence': 'high',
                'current_value': f"{metrics['open_rate']:.1f}%",
                'target_value': '25-30%'
            })
        
        # Analyze reply rate
        if metrics['reply_rate'] < 2:
            recommendations.append({
                'category': 'Email Content',
                'suggestion': 'Reply rate is low. Try shorter emails (under 100 words), clearer value propositions, and more specific CTAs.',
                'confidence': 'high',
                'current_value': f"{metrics['reply_rate']:.1f}%",
                'target_value': '3-5%'
            })
        
        # Analyze meeting booking rate
        if metrics['meeting_rate'] < 0.5 and metrics['reply_rate'] > 2:
            recommendations.append({
                'category': 'Call-to-Action',
                'suggestion': 'Good reply rate but low meeting bookings. Make CTAs more specific (e.g., "15-min call Tuesday 2pm?") and include calendar links.',
                'confidence': 'medium',
                'current_value': f"{metrics['meeting_rate']:.1f}%",
                'target_value': '1-2%'
            })
        
        # Analyze lead scoring effectiveness
        avg_score = sum(lead.get('score', 0) for lead in scored_leads) / len(scored_leads) if scored_leads else 0
        if avg_score < 70:
            recommendations.append({
                'category': 'ICP Targeting',
                'suggestion': 'Average lead score is below 70. Consider tightening ICP criteria to focus on higher-quality prospects.',
                'confidence': 'medium',
                'current_value': f"{avg_score:.1f}",
                'target_value': '75+'
            })
        
        # Positive feedback
        if metrics['open_rate'] > 25:
            recommendations.append({
                'category': 'Subject Lines',
                'suggestion': 'Subject lines are performing well! Document winning patterns and continue A/B testing.',
                'confidence': 'high',
                'current_value': f"{metrics['open_rate']:.1f}%",
                'target_value': 'Maintain'
            })
        
        if metrics['meeting_rate'] > 1:
            recommendations.append({
                'category': 'Overall Performance',
                'suggestion': 'Excellent meeting booking rate! Scale this campaign and document the messaging approach.',
                'confidence': 'high',
                'current_value': f"{metrics['meeting_rate']:.1f}%",
                'target_value': 'Scale'
            })
        
        return recommendations
    
    def _save_to_sheets(self, metrics: Dict, recommendations: List[Dict]):
        """
        Save metrics and recommendations to Google Sheets
        
        Args:
            metrics: Performance metrics
            recommendations: Generated recommendations
        """
        if 'GoogleSheets' not in self.tools_config:
            self.observe("Google Sheets not configured, saving to local file")
            self._save_to_local_file(metrics, recommendations)
            return
        
        try:
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials
            
            # This is a placeholder for actual Google Sheets integration
            # In production, you would:
            # 1. Authenticate with service account
            # 2. Open the spreadsheet
            # 3. Write metrics and recommendations
            
            self.act("Saving to Google Sheets")
            self.observe("⚠️  Google Sheets integration not fully configured, saving locally")
            self._save_to_local_file(metrics, recommendations)
            
        except Exception as e:
            self.observe(f"Google Sheets error: {str(e)}")
            self._save_to_local_file(metrics, recommendations)
    
    def _save_to_local_file(self, metrics: Dict, recommendations: List[Dict]):
        """Save feedback to local JSON file"""
        import os
        
        os.makedirs('data', exist_ok=True)
        
        feedback_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'recommendations': recommendations
        }
        
        filename = f"data/feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        self.observe(f"[+] Feedback saved to {filename}")
        
        # Also print recommendations to console
        print("\n" + "="*60)
        print("[RECOMMENDATIONS] CAMPAIGN ANALYSIS")
        print("="*60)
        for rec in recommendations:
            print(f"\n[{rec['category'].upper()}]")
            print(f"  {rec['suggestion']}")
            print(f"  Current: {rec['current_value']} -> Target: {rec['target_value']}")
            print(f"  Confidence: {rec['confidence']}")
        print("="*60 + "\n")