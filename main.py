import logging
from job_application.config import Config
from job_application.database import JobDatabase
from job_application.email_manager import EmailManager
from job_application.application import ApplicationManager  # ✅ Fixed line
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
    application_manager = ApplicationManager(config, job_db, email_manager)
    stats = AgentStatistics(job_db)

    try:
        # Process applications
        logger.info("Processing applications...")
        applications_sent = application_manager.process_applications()
        logger.info(f"Application processing completed. Sent {applications_sent} applications.")

        # Process follow-ups
        logger.info("Processing follow-ups...")
        follow_ups_sent = application_manager.process_follow_ups()
        logger.info(f"Follow-up processing completed. Sent {follow_ups_sent} follow-ups.")

        # Generate statistics
        stats.save_report()
        stats.generate_excel_report()

    except Exception as e:
        logger.error(f"An error occurred in the main process: {e}")


if __name__ == "__main__":
    main()