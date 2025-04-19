import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from job_application.scrapers.base import JobScraper
from job_application.email_manager import EmailExtractor

logger = logging.getLogger(__name__)

class IndeedScraper(JobScraper):
    """Scraper for Indeed job postings."""
    
    def scrape_jobs(self, job_title, location):
        """Scrape Indeed jobs."""
        if not self.driver:
            self._initialize_driver()
            
        jobs = []
        logger.info(f"Searching Indeed for {job_title} in {location}")
        
        # Format the job title and location for the URL
        formatted_job = job_title.replace(' ', '+')
        formatted_location = location.replace(' ', '+')
        
        url = f"https://www.indeed.com/jobs?q={formatted_job}&l={formatted_location}&fromage=7"
        
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for the page to load
            
            # Extract             # Extract    job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")
            
            for card in job_cards:
                try:
                    # Get job title
                    title_element = card.find_element(By.CSS_SELECTOR, "h2.jobTitle span")
                    title = title_element.text
                    
                    # Get company name
                    company_element = card.find_element(By.CSS_SELECTOR, ".companyName")
                    company = company_element.text
                    
                    # Get job link
                    link_element = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
                    link = link_element.get_attribute("href")
                    
                    # Get job details by clicking on the job
                    title_element.click()
                    time.sleep(2)
                    
                    # Switch to the job description iframe
                    self.driver.switch_to.frame(self.driver.find_element(By.ID, "vjs-container-iframe"))
                    
                    # Extract job description
                    description_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "jobDescriptionText"))
                    )
                    description = description_element.text
                    
                                                                                      switch_to.default_content()
                    
                    # Extract emails from description
                    emails = EmailExtractor.extract_emails(description)
                    
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'url': link,
                        'description': description,
                        'emails': emails,
                                                                                                             s.append(job_data)
                except Exception as e:
                    logger.error(f"Error extracting job details from Indeed: {e}")
                    # Switch back to the main content in case of error
                    self.driver.switch_to.default_content()
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
        
        return jobs
