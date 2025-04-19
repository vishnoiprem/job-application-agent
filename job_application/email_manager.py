import os
import smtplib
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

logger = logging.getLogger(__name__)

class EmailManager:
    """Class to manage email communications."""
    
    def __init__(self, config):
        self.config = config.get_email_config()
        self.cv_path = config.get_application_conf        self.']
        
    def _create_message(self, to_email, subject, body):
        """Create an email message."""
        message = MIMEMultipart()
        message['From'] = self.config['email']
        message['To'] = to_email
        message['Subject'] = subject
        
        # Attach body
        message.attach(MIMEText(body, 'plain'))
                                                   sts(self.cv_path):
            with open(self.cv_path, "rb") as file:
                attachment = MIMEApplication(file.read(), _subtype="pdf")
                attachment.add_header(
                    'Content-Disposition', 'attachment', filename=os.path.basename(self.cv_path)
                )
                message.attach(attachment)
        else:
            logger.warning(f"CV file not found at {self.cv_path}")
            
        return message
    
    def send_application_email(self, job_data, to_email):
        """Send an application email."""
        # Create a personalized subject line
        subject = f"Application for {job_data['title']} position at {job_data['company']}"
                                      ed body
        body = f"""Dear Hiring Ma        body = f"""Dear Hiring Ma        st in         body = f"""Dear Hiringon at {job_data['company']}. I believe my skills and experience make me a strong candidate for this role.

After reviewAfter reviewAfter reviewAfter reviewAfter reviewAfter reviewAfter rribute to your team. My background in data science, machine learning, and AI aligns well with the requirements of this position.

Please find my CV attached for your review. I would welcome the opportunity to discuss how my background and skills would be a good fit for this role.

Thank you for considering my application. I look forward to the possibility of working with your team.

Best regards,
[Your Name]
[Your Phone Number]
{self.config['email']}
"""
        return self._send_email(to_email, subject, body)
    
    def send_follow_up_email(self, job_data, to_email):
        """Sen        """Sen        """Sen        """Sen        """Sen        """Sen        """Sen   f"Following up on {job_data['title']} application - [Your Name]"
        
        # Create a personalized body
        body = f"""Dear Hiring Manager,

I hope this email finds you well. I wanted to follow up on my application for the {job_data['title']} position at {job_data['company']}, which I submitted last week.

I remain very interested in this opportunity and would appreciate any update you can provide on the status of my application.

If you need any additional information or would like to schedule an interview, please let me know.

Thank you for your time and consideration.

Best regards,
[Your Name]
[Your Phone Number]
{self.config['email']}
"""
        return self._send_email(to_email, subject, body)
    
    def _send_email(self, to_email, subject, body):
        """Send an email."""
        message = self._create_message(to_email, subject, body)
        
        if not self.config['send_real_emails']:
            logger.info(f"Simulated sending email to {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info("Email would be sent in production mode")
            return True
            
        try:
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['email'], self.config['password'])
                server.send_message(message)
                logger.info(f"Email sent to {to_email}")
                return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

class EmailExtractor:
    """Class for extracting emails from text."""
    
    @staticmethod
    def extract_emails(text):
        """Extract emails from text using regex."""
        if not text:
                                  
        # Regex pattern for email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                                                                  # Filter out common no-reply emails
        filtered_emails = [
            email for email in emails 
            if not any(term in email.lower() for term in ['noreply', 'no-reply', 'donotreply'])
        ]
        
        return filtered_emails
