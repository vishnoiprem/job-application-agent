import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from job_application.scrapers.base import JobScraper
from job_application.email_manager import EmailExtractor

logger = logging.getLogger(__name__)

class LinkedInScraper(JobScraper):
    """Scraper for LinkedIn job postings."""
    
    def scrape_jobs(self, job_title, location):
        """Scrape LinkedIn jobs."""
        if not self.driver:
            self._initialize_driver()
            
        jobs = []
        logger.info(f"Searching LinkedIn for {job_title} in {location}")
        
        # Format the job title and location for the URL
        formatted_job = job_title.replace(' ', '%20')
        formatted_location = location.replace(' ', '%20')
        
        url = f"https://www.linkedin.com/jobs/search/?keywords={formatted_job}&location={formatted_location}&f_TPR=r604800"
        
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for the page to load
            
            # Scroll to load more jobs
            for _ in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            
            # Extract job listings
            job_cards = self.driver.find_elements(By.CLASS_NAME, "job-card-container")
            
            for card in job_cards:
                try:
                    # Get job title
                    title_element = card.find_element(By.CLASS_NAME, "job-card-list__title")
                    title = title_element.text
                    
                    # Get company name
                    company_element = card.find_element(By.CLASS_NAME, "job-card-container__company-name")
                    company = company_element.text
                    
                    # Get job link
                    link_element = card.find_element(By.CLASS_NAME, "job-card-list__title")
                    link = link_element.get_attribute("href")
                    
                    # Get job details by clicking on the job
                    title_element.click()
                    time.sleep(2)
                    
                    # Extract job description
                    description_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "description__text"))
                    )
                    description = description_element.text
                    
                    # Extract emails from description
                    emails = EmailExtractor.extract_emails(description)
                    
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'url': link,
                        'description': description,
                        'emails': emails,
                        'source': 'linkedin'
                    }
                                         jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error extracting job details: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
        
        return jobs
