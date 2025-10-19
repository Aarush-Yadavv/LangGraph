from typing import Dict, Any, List
from datetime import datetime
import uuid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from . import BaseAgent


class OutreachExecutorAgent(BaseAgent):
    """
    Agent responsible for executing email outreach
    Uses SendGrid API (or simulates in dry-run mode)
    """
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send outreach emails to leads
        
        Args:
            inputs: Contains 'messages' array and 'dry_run' flag
            
        Returns:
            Dictionary with 'campaign_id' and 'sent_status' array
        """
        self.think("Starting email outreach execution")
        
        messages = inputs.get('messages', [])
        dry_run = inputs.get('dry_run', True)
        
        self.think(f"Preparing to send {len(messages)} emails")
        
        if dry_run:
            self.observe("⚠️  DRY RUN MODE - No emails will actually be sent")
        
        campaign_id = f"campaign_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d')}"
        
        sent_status = []
        
        for message in messages:
            self.act(f"Processing email to {message.get('lead')} at {message.get('email')}")
            
            if dry_run:
                status = self._simulate_send(message)
            else:
                status = self._send_with_sendgrid(message)
            
            sent_status.append(status)
            self.observe(f"Email to {message.get('lead')}: {status['status']}")
        
        success_count = sum(1 for s in sent_status if s['status'] in ['sent', 'simulated'])
        self.observe(f"Campaign complete: {success_count}/{len(messages)} emails processed")
        
        output = {
            'campaign_id': campaign_id,
            'sent_status': sent_status
        }
        
        self.validate_output(output)
        return output
    
    def _simulate_send(self, message: Dict) -> Dict[str, Any]:
        """Simulate email sending for dry-run mode"""
        return {
            'email': message.get('email'),
            'lead': message.get('lead'),
            'company': message.get('company'),
            'status': 'simulated',
            'timestamp': datetime.now().isoformat(),
            'message_id': f"sim_{uuid.uuid4().hex[:12]}"
        }
    
    def _send_with_sendgrid(self, message: Dict) -> Dict[str, Any]:
        """Send email using SendGrid API"""
        if 'SendGrid' not in self.tools_config:
            return {
                'email': message.get('email'),
                'lead': message.get('lead'),
                'status': 'failed',
                'error': 'SendGrid not configured',
                'timestamp': datetime.now().isoformat()
            }
        
        config = self.tools_config['SendGrid']
        api_key = config.get('api_key')
        from_email = config.get('from_email')
        from_name = config.get('from_name')
        
        if not api_key or api_key == '':
            return {
                'email': message.get('email'),
                'lead': message.get('lead'),
                'status': 'failed',
                'error': 'SendGrid API key not set',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            sg_message = Mail(
                from_email=(from_email, from_name),
                to_emails=message.get('email'),
                subject=message.get('subject'),
                plain_text_content=message.get('email_body')
            )
            
            sg = SendGridAPIClient(api_key)
            response = sg.send(sg_message)
            
            return {
                'email': message.get('email'),
                'lead': message.get('lead'),
                'company': message.get('company'),
                'status': 'sent',
                'timestamp': datetime.now().isoformat(),
                'message_id': response.headers.get('X-Message-Id', 'unknown'),
                'status_code': response.status_code
            }
            
        except Exception as e:
            return {
                'email': message.get('email'),
                'lead': message.get('lead'),
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }