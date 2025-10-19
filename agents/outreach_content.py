from typing import Dict, Any, List
from openai import OpenAI
import os
from . import BaseAgent


class OutreachContentAgent(BaseAgent):
    """
    Agent responsible for generating personalized outreach content
    Uses OpenAI GPT-4o-mini to create compelling emails
    """
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized outreach messages for each lead
        
        Args:
            inputs: Contains 'ranked_leads', 'persona', and 'tone'
            
        Returns:
            Dictionary with 'messages' array containing email content
        """
        self.think("Starting outreach content generation")
        
        ranked_leads = inputs.get('ranked_leads', [])
        persona = inputs.get('persona', 'SDR')
        tone = inputs.get('tone', 'friendly and professional')
        
        self.think(f"Generating personalized emails for {len(ranked_leads)} leads")
        self.think(f"Persona: {persona}, Tone: {tone}")
        
        messages = []
        
        for lead in ranked_leads:
            self.act(f"Generating email for {lead.get('contact')} at {lead.get('company')}")
            
            email_content = self._generate_email(lead, persona, tone)
            
            message = {
                'lead': lead.get('contact'),
                'email': lead.get('email'),
                'subject': email_content['subject'],
                'email_body': email_content['body'],
                'company': lead.get('company')
            }
            
            messages.append(message)
            self.observe(f"Generated email for {lead.get('contact')}")
        
        self.observe(f"Successfully generated {len(messages)} personalized emails")
        
        output = {'messages': messages}
        self.validate_output(output)
        
        return output
    
    def _generate_email(self, lead: Dict, persona: str, tone: str) -> Dict[str, str]:
        """
        Generate email using OpenAI or fallback to template
        
        Args:
            lead: Lead information
            persona: Email persona (SDR, AE, etc.)
            tone: Email tone
            
        Returns:
            Dictionary with 'subject' and 'body'
        """
        # Try OpenAI first
        if 'OpenAI' in self.tools_config:
            openai_result = self._generate_with_openai(lead, persona, tone)
            if openai_result:
                return openai_result
        
        # Fallback to template
        self.observe("Using template-based email generation")
        return self._generate_template_email(lead, persona)
    
    def _generate_with_openai(self, lead: Dict, persona: str, tone: str) -> Dict[str, str]:
        """Generate email using OpenAI API"""
        api_config = self.tools_config.get('OpenAI', {})
        api_key = api_config.get('api_key')
        
        if not api_key or api_key == '':
            return None
        
        try:
            client = OpenAI(api_key=api_key)
            
            # Create prompt
            prompt = f"""You are a {persona} writing a personalized outreach email.

Lead Information:
- Name: {lead.get('contact')}
- Role: {lead.get('role')}
- Company: {lead.get('company')}
- Company Description: {lead.get('company_description', 'N/A')}
- Recent News: {lead.get('recent_news', 'N/A')}
- Technologies: {', '.join(lead.get('technologies', []))}
- Lead Score: {lead.get('score')}/100

Task:
Write a {tone} outreach email to this prospect. The email should:
1. Be personalized based on their company and recent news
2. Be concise (under 150 words)
3. Have a clear value proposition
4. Include a specific call-to-action (schedule a 15-min call)
5. Sound natural and human, not salesy

Product: Analytos.ai - AI-powered sales analytics and lead generation platform

Return ONLY two things:
SUBJECT: [subject line here]
BODY: [email body here]
"""
            
            response = client.chat.completions.create(
                model=api_config.get('model', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": "You are an expert sales copywriter who writes compelling, personalized outreach emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse response
            lines = content.split('\n')
            subject = ''
            body = ''
            
            for i, line in enumerate(lines):
                if line.startswith('SUBJECT:'):
                    subject = line.replace('SUBJECT:', '').strip()
                elif line.startswith('BODY:'):
                    body = '\n'.join(lines[i+1:]).strip()
                    break
            
            if not body:
                body = content
            
            return {
                'subject': subject or self._generate_subject(lead),
                'body': body
            }
            
        except Exception as e:
            self.observe(f"OpenAI API error: {str(e)}")
            return None
    
    def _generate_template_email(self, lead: Dict, persona: str) -> Dict[str, str]:
        """Generate email using template"""
        
        subject = self._generate_subject(lead)
        
        body = f"""Hi {lead.get('contact').split()[0]},

I noticed {lead.get('company')} recently {lead.get('recent_news', 'has been growing').lower()}.

At Analytos.ai, we help B2B companies like {lead.get('company')} streamline their lead generation process using AI-powered analytics. Our platform has helped similar companies increase qualified leads by 40% while reducing manual research time by 60%.

Given {lead.get('company')}'s growth trajectory and your role as {lead.get('role')}, I thought this might be relevant for your team.

Would you be open to a quick 15-minute call next week to explore how we could help {lead.get('company')} scale your sales efforts more efficiently?

Best regards,
Sales Team
Analytos.ai"""
        
        return {
            'subject': subject,
            'body': body
        }
    
    def _generate_subject(self, lead: Dict) -> str:
        """Generate email subject line"""
        
        subjects = [
            f"Quick question about {lead.get('company')}'s sales process",
            f"Helping {lead.get('company')} scale lead generation",
            f"{lead.get('contact').split()[0]}, thoughts on AI-powered sales?",
            f"Scaling sales at {lead.get('company')}",
            f"Re: {lead.get('company')}'s recent growth"
        ]
        
        import random
        return random.choice(subjects)