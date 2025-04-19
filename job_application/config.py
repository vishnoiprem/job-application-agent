import os
import configparser

class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        
        # Create default config if it doesn't exist
        if not os.path.exists(config_file):
            self._create_default_config()
            
        self.config.read(config_file)
        self.config_file = config_file
        
    def _create_default_config(self):
        """Create a default configuration file."""
        self.config['EMAIL'] = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': '587',
            'email': 'your.email@gmail.com',
            'password': 'your_app_password',  # Use app password for Gmail
            'send_real_emails': 'False'
        }
        
        self.config['JOB_SEARCH'] = {
            'job_titles': 'Data Engineer, AI Engineer, Head of Data, Machine Learning Engineer',
            'locations': 'Remote, New York, London, Singapore, Hong Kong, Vietnam, Thailand',
            'days_old': '7',
            'blacklisted_companies': 'Company1, Company2',
            'search_linkedin': 'True',
            'search_indeed': 'True',
            'search_glassdoor': 'True',
            'search_interval_minutes': '60'
        }
        
        self.config['APPLICATION'] = {
            'cv_path': 'data/resumes/my_resume.pdf',
            'follow_up_days': '7',
            'max_applications_per_day': '10',
            'application_delay_minutes': '15'
        }
        
        with open('config.ini', 'w') as f:
            self.config.write(f)
    
    def get_email_config(self):
        """Get email configuration."""
        return {
            'smtp_server': self.config['EMAIL']['smtp_server'],
            'smtp_port': int(self.config['EMAIL']['smtp_port']),
            'email': self.config['EMAIL']['email'],
            'password': self.config['EMAIL']['password'],
            'send_real_emails': self.config['EMAIL'].getboolean('send_real_emails')
        }
    
    def get_job_search_config(self):
        """Get job search configuration."""
        return {
            'job_titles': [title.strip() for title in self.config['JOB_SEARCH']['job_titles'].split(',')],
            'locations': [loc.strip() for loc in self.config['JOB_SEARCH']['locations'].split(',')],
            'days_old': int(self.config['JOB_SEARCH']['days_old']),
            'blacklisted_companies': [company.strip() for company in self.config['JOB_SEARCH']['blacklisted_companies'].split(',')],
            'search_linkedin': self.config['JOB_SEARCH'].getboolean('search_linkedin'),
            'search_indeed': self.config['JOB_SEARCH'].getboolean('search_indeed'),
            'search_glassdoor': self.config['JOB_SEARCH'].getboolean('search_glassdoor'),
            'search_interval_minutes': int(self.config['JOB_SEARCH']['search_interval_minutes'])
        }
    
    def get_application_config(self):
        """Get application configuration."""
        return {
            'cv_path': self.config['APPLICATION']['cv_path'],
            'follow_up_days': int(self.config['APPLICATION']['follow_up_days']),
            'max_applications_per_day': int(self.config['APPLICATION']['max_applications_per_day']),
            'application_delay_minutes': int(self.config['APPLICATION']['application_delay_minutes'])
        }
    
    def save(self):
        """Save the configuration to file."""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
