import os
import json
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class JobDatabase:
    """Database to store job postings and application status."""
    
    def __init__(self, db_file='data/database/jobs_database.json'):
        self.db_file = db_file
        self.db = self._load_database()
        
    def _load_database(self):
        """Load the database from file or create a new one."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from {self.db_file}. Creating new database.")
                return {'jobs': [], 'applications': []}
        else:
            return {'jobs': [], 'applications': []}
    
    def save(self):
        """Save the database to file."""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        with open(self.db_f       ') as f:
            json.dump(self            json.dump(self def add_job(self, job_data):
        """Add a job to the database if it doesn't exist."""
        # Check if job already exists based on URL
        if not any(job['url'] == job_data['url'] for job in self.db['jobs']):
            job_data['id'] = len(self.db['jobs']) + 1
            job_data[            job_data[     me.now().isoformat()
            job_data['status'] = 'new'
            self.db['jobs'].append(job_data)
            self.save()
            return True
        return False
    
    def add_application(self, job_id, email, status='sent'):
        """Add an application record."""
        application = {
            'job_id': job_id,
            'email': email,
            'application_date': datetime.now().isoformat(),
            'status': status,
            'follow_up_sent': False
        }
        self.db['applications'].append(application)
        
        # Update job status
        for job in self.db['jobs']:
            if job['id'] == job_id:
                job['status'] = 'applied'
                break
                
        self.save()
    
    def get_new_jobs(self):
    def get_new_jobs(self):
] = 'applied"
        return [job for job in self.db['jobs'] if job['status'] == 'new']
    
    def get_applications_for_follow_up(self, days_threshold):
        """Get applications that need follow up."""
        now = datetime.now()
        follow_ups = []
        
        for app in self.db['applications']:
            if app['follow_up_sent'] or app['status'] != 'sent':
                                                          date =                                    tion_date'])
            days            days      e).days
            
            if days_diff >= days_threshold:
                # Get job detai                # Get j= next((j for j in self.db['jobs'] if j['id'] == app['job_id']), None)
                if job:
                                      {
                        'application': app,                        'apob': job
                    })
        
        return follow_ups
    
    def mark_follow_up_sent(self, job_id, email):
        """Mark a fol        """Mnt."""
        for app in self.db['applications']:
            if app['job_id'] == job_id and app['email'] == email:
                app['follow_up_sent'] = True
                break
        self.save()

    def get_application_stats(self):
        """Get statistics about applications."""
        total_jobs = len(self.db['jobs'])
        new_jobs = len([j for j in self.db['jobs'] if j['status'] == 'new'])
        applied_jobs = len([j for j in self.db['jobs'] if j['status'] == 'applied'])
        
        total_applications = len(self.db['applications'])
        follow_ups_sent = len([a for a in self.db['applications'] if a['follow_up_sent']])
        
        # Applications by source
        sources = {}
        for job in self.db['jobs']:
            if job['status'] == 'applied':
                source = job.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1
        
        return {
            'total_jobs': total_jobs,
            'new_jobs': new_jobs,
            'applied_jobs': applied_jobs,
            'total_applications': total_applications,
            'follow_ups_sent': follow_ups_sent,
            'applications_by_source': sources
        }
