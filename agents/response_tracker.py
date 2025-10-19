from typing import Dict, Any, List
import random
from datetime import datetime
from . import BaseAgent


class ResponseTrackerAgent(BaseAgent):
    """
    Agent responsible for tracking email responses and engagement
    Monitors opens, clicks, replies, and meeting bookings
    """
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track email engagement metrics
        
        Args:
            inputs: Contains 'campaign_id' and 'sent_status'
            
        Returns:
            Dictionary with 'responses' array containing engagement data
        """
        self.think("Starting response tracking for email campaign")
        
        campaign_id = inputs.get('campaign_id')
        sent_status = inputs.get('sent_status', [])
        
        self.think(f"Tracking responses for campaign: {campaign_id}")
        self.think(f"Monitoring {len(sent_status)} emails")
        
        responses = []
        
        for status in sent_status:
            if status.get('status') in ['sent', 'simulated']:
                self.act(f"Tracking engagement for {status.get('email')}")
                
                # In a real system, this would query SendGrid/Apollo APIs
                # For this demo, we simulate realistic engagement metrics
                engagement = self._simulate_engagement(status)
                responses.append(engagement)
                
                self.observe(f"{status.get('email')}: "
                           f"Opened={engagement['opened']}, "
                           f"Replied={engagement['replied']}")
        
        # Calculate overall metrics
        total = len(responses)
        opened = sum(1 for r in responses if r['opened'])
        clicked = sum(1 for r in responses if r['clicked'])
        replied = sum(1 for r in responses if r['replied'])
        meetings = sum(1 for r in responses if r['meeting_booked'])
        
        self.observe(f"Campaign metrics: "
                    f"Open rate: {opened/total*100:.1f}%, "
                    f"Reply rate: {replied/total*100:.1f}%, "
                    f"Meeting rate: {meetings/total*100:.1f}%")
        
        output = {'responses': responses}
        self.validate_output(output)
        
        return output
    
    def _simulate_engagement(self, email_status: Dict) -> Dict[str, Any]:
        """
        Simulate realistic email engagement metrics
        
        In production, this would call SendGrid/Apollo APIs to get real data
        
        Args:
            email_status: Email send status
            
        Returns:
            Engagement metrics dictionary
        """
        # Realistic engagement rates for B2B cold emails
        # Open rate: ~20-30%
        # Click rate: ~2-5% of opens
        # Reply rate: ~1-3%
        # Meeting rate: ~0.5-1%
        
        opened = random.random() < 0.25  # 25% open rate
        clicked = opened and random.random() < 0.15  # 15% of opens click
        replied = opened and random.random() < 0.08  # 8% of opens reply
        meeting_booked = replied and random.random() < 0.3  # 30% of replies book meeting
        
        engagement = {
            'email': email_status.get('email'),
            'lead': email_status.get('lead'),
            'company': email_status.get('company'),
            'opened': opened,
            'clicked': clicked,
            'replied': replied,
            'meeting_booked': meeting_booked,
            'open_timestamp': datetime.now().isoformat() if opened else None,
            'reply_timestamp': datetime.now().isoformat() if replied else None
        }
        
        # Add reply content for positive responses
        if replied:
            engagement['reply_content'] = self._generate_mock_reply(meeting_booked)
        
        return engagement
    
    def _generate_mock_reply(self, positive: bool) -> str:
        """Generate mock reply content"""
        
        if positive:
            positive_replies = [
                "Thanks for reaching out! I'd be interested in learning more. Do you have time for a call next week?",
                "This looks interesting. Let's schedule a 15-minute call to discuss further.",
                "I'm interested. Can you send me some more information and your calendar link?",
                "This could be relevant for our team. Let's connect next Tuesday if you're available."
            ]
            return random.choice(positive_replies)
        else:
            neutral_replies = [
                "Thanks for the email. Can you send me more details about your solution?",
                "Interesting. We're not looking right now but keep me posted.",
                "I'll review this with my team and get back to you.",
                "Not a priority at the moment, but let's revisit in Q2."
            ]
            return random.choice(neutral_replies)
    
    def _track_with_apollo_api(self, campaign_id: str) -> List[Dict]:
        """
        Track responses using Apollo API (for production use)
        
        This is a placeholder for actual API integration
        """
        # In production, you would:
        # 1. Call Apollo API to get campaign statistics
        # 2. Parse email opens, clicks, replies
        # 3. Track meeting bookings
        
        pass