import re

def extract_emails(text):
    """Extract emails from text using regex."""
    if not text:
        return []
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    filtered_emails = [
        email for email in emails
        if not any(term in email.lower() for term in ['noreply', 'no-reply', 'donotreply'])
    ]
    return filtered_emails

# Paste job description text here
job_text = """
[Paste the job description text here from LinkedIn or elsewhere]
"""

emails = extract_emails(job_text)
print("Found emails:", emails)
