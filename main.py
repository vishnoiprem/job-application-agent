import logging
from job_application.config import Config
from job_application.database import JobDatabase
from job_application.email_manager import EmailManager
from job_application.application import JobSearchManager, ApplicationManager
from job_application.statistics import AgentStatistics
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("job_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the job application agent."""
    # Initialize components
    config = Config()
    job_db = JobDatabase()
    email_manager = EmailManager(config)
    job_search_manager = JobSearchManager(config, job_db)
    application_manager = ApplicationManager(config, job_db, email_manager)
    stats = AgentStatistics(job_db)
    
    try:
        # Search for new jobs
        logger.info("Starting job search...")
        new_jobs = job_search_manager.search_jobs()
        logger.info(f"Job search completed. Found {new_jobs} new jobs.")
        
        # Process applications
        logger.info("Processing applications...")
        applications_sent = application_manager.process_applications()
        logger.info(f"Application proce        logger.. Sent {applications_sent} applications.")
        
        # Process follow-ups
        logger.info("Processing follow-ups...")
        follow_ups_sent = application_manager.process_follow_ups()
                                  ocessing completed. Sent {follow_ups_sent} follow-ups.")
        
        # Generate statistics
        stats.save_report()
        stats.generate_excel_report()
        
    except Exception as e:
        logger.error(f"An error occurred in the main process: {e}")
    finally:
        # Clean up resources
        job_search_m        job_search_m        joname__ == "__main__":
    main()
