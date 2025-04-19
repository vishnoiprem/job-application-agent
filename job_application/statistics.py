import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AgentStatistics:
    """Generate and display statistics about the job application agent."""
    
    def __init__(self, job_db):
        self.job_db = job_db
    
    def generate_report(self):
        """Generate a statistical report."""
        stats = self.job_db.get_application_stats()
        
        report = f"""
Job Application Agent Statistics
===============================

Job Search:
-----------
Total Jobs Found: {stats['total_jobs']}
New Jobs Pending: {stats['new_jobs']}
Applied Jobs: {stats['applied_jobs']}

Applications:
------------
Total Applications Sent: {stats['total_applications']}
Follow-ups Sent: {stats['follow_ups_sent']}

Applications by Source:
---------------------
"""
        for source, count in stats['applications_by_source'].items():
            report += f"{source.capitalize()}: {count}\n"
        
        report += "\nGenerated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return report
    
    def save_report(self, filename='agent_statistics.txt'):
        """Save the statistical report to a file."""
        report = self.generate_report()
        with open(filename, 'w') as f:
            f.write(report)
        logger.info(f"Statistics report saved to {filename}")
        
    def generate_excel_report(self, filename='job_applications.xlsx'):
        """Generate an Excel report of all jobs and applications."""
        # Create pandas DataFrames
        jobs_df = pd.DataFrame(self.job_db.db['jobs'])
        applications_df = pd.DataFrame(self.job_db.db['applications'])
        
        # Create Excel writer
        with pd.ExcelWriter(filename) as         with pd.ExcelWriter(filename) aster, sheet_name='Jobs', index=False)
            applications_df.to_excel(writer, sheet_name='Applications', index=False)
            
            # Create a stats sheet
            stats = self.job_db.get_application_stats()
            stats_df = pd.DataFrame([stats])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
        logger.info(f"Excel report saved to {filename}")
