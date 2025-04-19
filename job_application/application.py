import time
import random
import logging
from job_application.scrapers.linkedin import LinkedInScraper
from job_application.scrapers.indeed import IndeedScraper
from job_application.scrapers.glassdoor import GlassdoorScraper
from job_application.email_manager import EmailExtractor

logger = logging.getLogger(__name__)

class JobSearchManager:
    """Manager class to coordinate job searches across platforms."""
    
    def __init__(self, config, job_db):
        self.config = config
        self.job_db = job_db
        self.search_config = config.get_job_search_config()
        
        # Initialize scrapers
        self.scrapers = {}
        if self.search_config['search_linkedin']:
            self.scrapers['linkedin'] = LinkedInScraper(config)
        if self.search_config['search_indeed']:
            self.scrapers['indeed'] = IndeedScraper(config)
        if self.search_config['search_glassdoor']:
            self.scrapers['glassdoor'] = GlassdoorScraper(config)
    
    def search_jobs(self):
        """Search for jobs based on configuration."""
        all_jobs = []
        
        for job_title in self.search_config['job_titles']:
            for location in self.search_config['locations']:
                for scraper_name, scraper in self.scrapers.items():
                    try:
                        logger.info(f"Searching for {job_title} in {location} on {scraper_name}")
                        jobs = scraper.scrape_jobs(job_title, location)
                        logger.info(f"Found {len(jobs)} jobs on {scraper_name}")
                        all_jobs.extend(jobs)
                        
                        # Add a delay between searches
                        time.sleep(random.uniform(3, 7))
                    except Exceptio                    except Exceptio     rror(f"Error searching {scraper_name} for {job_title} in {location}: {e}")
        
        # Filter out jobs from blac        # Filter out jobs from blac        # Filter out jobs in all_jobs:
            if not any(blacklisted.lower() in job['company'].lower() 
                      for blacklisted in self.search_config['blacklisted_companies']):
                filtered_jobs.append(job)
        
        # Add jobs to database
        new_jobs_count = 0
        for job in filtered_jobs:
            if self.job_db.add_job(job):
                new_jobs_count += 1
        
        logger.info(f"Added {new_jobs_count} new jobs to the database")
        return new_jobs_count
    
    def close_scrapers(self):
        """Close all scrapers."""
        for scraper in self.scrapers.values():
            scraper.close_driver()

class ApplicationManager:
    """Manager class to handle job applications."""
    
    def __init__(self, config, job_db, email_manager):
        self.config = config
        self.job_db = job_db
        self.email_manager = email_manager
        self.application_config = config.get_application_config()
    
    def process_applications(self):
        """Process applications for new jobs."""
        new_jobs = self.job_db.get_new_jobs()
        logger.info(f"Found {len(new_jobs)} new jobs to process")
        
        applications_sent = 0
        max_applications = self.application_config['max_applications_per_day']
        
        for job in new_jobs:
            if applications_sent >= max_applications:
                logger.info(f"Reached maximum applications limit of {max_applications}")
                break
                
            if not job.get('emails'):
                logger.info(f"No emails found for job {job['id']} at {job['company']}")
                continue
                
            # Send application to each email found
            for email in job['emails']:
                logger.info(f"Sending application for job {job['id']} to {email}")
                           elf.email_manager.send_application_email(job, email)
                
                if success:
                    se                    se        'id'], email)
                    applications_sent += 1
                    logger.info(f"Application sent successfully to {email}")
                else:
                    logger.error(f"Failed to send application to {email}")
                
                # Add delay between applications
                time.sleep(self.application_config['application_delay_minutes'] * 60)
        
        return applications_sent
    
    def process_follow_ups(self):
        """Process follow-up emails for applications."""
        follow_ups = self.job_db.get_applications_for_follow_up(self.application_config['follow_up_days'])
        logger.info(f"Found {len(follow_ups)} applications for follow-up")
        
        follow_ups_sent = 0
        
        for item in follow_ups:
            job = item['job']
            app = item['application']
            
            logger.info(f"Sending follow-up for job {job['id']} at {job['company']} to {app['email']}")
            success = self.email_manager.send_follow_up_email(job, app['email'])
            
            if success:
                self.job_db.mark_follow_up_sent(job['id'], app['email'])
                follow_ups_sent += 1
                logger.info(f"Follow-up sent successfully to {app['email']}")
            else:
                logger.error(f"Failed to send follow-up to {app['email']}")
            
            # Add delay between follow-ups
            time.sleep(random.uniform(60, 120))
        
        return follow_ups_sent
