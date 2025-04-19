import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from job_application.scrapers.base import JobScraper
from job_application.email_manager import EmailExtractor

logger = logging.getLogger(__name__)


class GlassdoorScraper(JobScraper):
    """Scraper for Glassdoor job postings."""

    def scrape_jobs(self, job_title, location):
        """Scrape Glassdoor jobs."""
        if not self.driver:
            self._initialize_driver()

        jobs = []
        logger.info(f"Searching Glassdoor for {job_title} in {location}")

        # Format the job title and location for the URL
        formatted_job = job_title.replace(' ', '-')
        formatted_location = location.replace(' ', '-')

        url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={formatted_job}&locT=C&locId=1127165&locKeyword={formatted_location}&fromAge=7"

        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for the page to load

            # Handle the sign-in popup if it appears
            try:
                close_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "span.SVGInline.modal_closeIcon"))
                )
                close_button.click()
            except:
                pass  # No popup or couldn't close it

            # Extract job listings
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".react-job-listing")

            for card in job_cards:
                try:
                    # Click on the job card to view details
                    card.click()
                    time.sleep(2)

                    # Get job title
                    title_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".jobViewMinimal .job-title"))
                    )
                    title = title_element.text

                    # Get company name
                    company_element = self.driver.find_element(By.CSS_SELECTOR, ".jobViewMinimal .employer-name")
                    company = company_element.text

                    # Get job URL
                    current_url = self.driver.current_url

                    # Extract job description
                    description_element = self.driver.find_element(By.CSS_SELECTOR, ".jobDescriptionContent")
                    description = description_element.text

                    # Extract emails from description
                    emails = EmailExtractor.extract_emails(description)

                    job_data = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'url': current_url,
                        'description': description,
                        'emails': emails,
                        'source': 'glassdoor'
                    }
                    print(job_data)
                    jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error extracting job details from Glassdoor: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping Glassdoor: {e}")

        return jobs
