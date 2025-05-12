import datetime
import logging
from job_application.email_handler import EmailConsolidator
from job_application.database import JobDatabase
from job_application.config import Config
from job_application.email_manager import EmailManager

logger = logging.getLogger(__name__)

def process_applications(jobs, applications, config):
    """Process job applications, consolidating emails to the same recipient."""

    new_jobs = [job for job in jobs if job["status"] == "new"]
    logger.info(f"Found {len(new_jobs)} new jobs to process")

    # Initialize email consolidator
    email_consolidator = EmailConsolidator()

    # Group jobs by email
    email_to_jobs = email_consolidator.consolidate_applications(jobs, applications)

    # Track new applications
    new_applications = []

    for email, job_ids in email_to_jobs.items():
        if not job_ids:
            continue

        # Skip already-applied emails
        already_applied = all(
            any(app.get("email") == email and app.get("job_id") == job_id for app in applications)
            for job_id in job_ids
        )
        if already_applied:
            logger.info(f"Skipping already-applied email: {email}")
            continue

        # Get job details
        job_details = []
        for job_id in job_ids:
            job = next((j for j in jobs if j["id"] == job_id), None)
            if job:
                job_details.append({
                    "id": job_id,
                    "company": job.get("company", "Unknown Company"),
                    "title": job.get("title", "Unknown Title")
                })

        if not job_details:
            continue

        # Create and send email
        email_data = email_consolidator.format_consolidated_email(
            email,
            job_details,
            config.get("user_profile", {})
        )
        email_consolidator.send_email(email_data)

        # Log new applications
        for job_id in job_ids:
            new_applications.append({
                "email": email,
                "job_id": job_id,
                "timestamp": datetime.datetime.now().isoformat()
            })

    return new_applications


class ApplicationManager:
    """Class wrapper for processing job applications."""

    def __init__(self, config: Config, job_db: JobDatabase, email_manager: EmailManager):
        self.config = config
        self.job_db = job_db
        self.email_manager = email_manager

    def process_applications(self):
        jobs = self.job_db.db.get("jobs", [])
        applications = self.job_db.db.get("applications", [])

        new_applications = process_applications(jobs, applications, self.config)

        self.job_db.db["applications"].extend(new_applications)
        self.job_db.save()

        return len(new_applications)

    def process_follow_ups(self):
        # Optional: add follow-up email automation here
        return 0