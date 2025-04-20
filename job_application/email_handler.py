import logging
import datetime
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class EmailConsolidator:
    def __init__(self):
        self.email_to_jobs = {}
        self.processed_emails = set()

    def consolidate_applications(self, jobs: List[Dict], applications: List[Dict]) -> Dict[str, List[int]]:
        """
        Group jobs by email address to send consolidated applications.

        Args:
            jobs: List of job listings
            applications: List of existing applications

        Returns:
            Dictionary mapping email addresses to lists of job IDs
        """
        # Reset state
        self.email_to_jobs = {}
        self.processed_emails = set()

        # Track emails that have already been sent
        for app in applications:
            if app.get("status") == "sent" and not app.get("follow_up_sent", False):
                self.processed_emails.add(app.get("email"))

        # Group new jobs by email
        for job in jobs:
            if job.get("status") == "new" and job.get("emails"):
                for email in job["emails"]:
                    # Skip if we've already applied to this email
                    if email in self.processed_emails:
                        continue

                    if email not in self.email_to_jobs:
                        self.email_to_jobs[email] = []

                    if job["id"] not in self.email_to_jobs[email]:
                        self.email_to_jobs[email].append(job["id"])

        return self.email_to_jobs

    def format_consolidated_email(self, email: str, job_details: List[Dict], user_profile: Dict) -> Dict:
        """
        Format a consolidated email for multiple job applications.

        Args:
            email: Recipient email address
            job_details: List of job details to include
            user_profile: User profile information

        Returns:
            Dictionary with email details
        """
        # Create subject line
        if len(job_details) == 1:
            subject = f"Application for {job_details[0].get('title', 'Data Engineer')} position"
        else:
            subject = f"Multiple Job Applications - {user_profile.get('name', 'Job Applicant')}"

        # Create email body
        body = f"Dear Hiring Manager,\n\n"

        if len(job_details) == 1:
            body += f"I am writing to express my interest in the {job_details[0].get('title', 'Data Engineer')} position at {job_details[0].get('company', 'your company')}."
        else:
            body += f"I am writing to express my interest in the following positions at your company:\n\n"
            for idx, job in enumerate(job_details, 1):
                body += f"{idx}. {job.get('title', 'Data Engineer')} at {job.get('company', 'your company')}\n"

        body += f"\n\nI have attached my resume for your consideration. "
        body += f"My background in {user_profile.get('background', 'Data Engineering')} and experience with "
        skills = user_profile.get('skills', ['Python', 'SQL', 'Data Pipelines'])[:3]
        body += f"{', '.join(skills)} align well with the requirements for these positions.\n\n"

        body += f"I am particularly interested in joining your team because of the innovative work you're doing in the data space.\n\n"

        body += f"Thank you for considering my application. I look forward to discussing how my skills and experience can benefit your team.\n\n"

        body += f"Best regards,\n{user_profile.get('name', 'Job Applicant')}\n"
        body += f"{user_profile.get('phone', '')}\n{user_profile.get('email', '')}"

        return {
            "to": email,
            "subject": subject,
            "body": body,
            "jobs": [j["id"] for j in job_details]
        }
