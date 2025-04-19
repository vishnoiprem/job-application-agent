import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, \
    ElementNotInteractableException
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
        logger.info(f"Accessing URL: {url}")

        try:
            self.driver.get(url)
            time.sleep(8)  # Longer wait for the page to load fully

            # Handle potential login prompt or popup with multiple attempts
            for attempt in range(3):
                try:
                    dismiss_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    "//button[contains(text(), 'Dismiss')] | //button[contains(text(), 'Close')] | //button[contains(@aria-label, 'Dismiss')] | //div[contains(@class, 'modal')]//button | //span[contains(text(), 'Maybe Later')]"))
                    )
                    self.driver.execute_script("arguments[0].click();", dismiss_button)
                    logger.info("Dismissed a popup on LinkedIn.")
                    time.sleep(2)
                except TimeoutException:
                    logger.info("No popup found on LinkedIn after waiting.")
                    break
                except Exception as e:
                    logger.warning(f"Error dismissing popup: {e}")
                    break

            # Scroll to load more jobs
            for i in range(300):  # Reduced scrolling to avoid overloading
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                logger.info(f"Scroll {i + 1}/3 to load more jobs.")

            # Extract job listings with multiple selector attempts
            job_cards = []
            selectors = [
                (By.CLASS_NAME, "job-card-container"),
                (By.CLASS_NAME, "jobs-search-results__list-item"),
                (By.CSS_SELECTOR, ".base-card")
            ]

            for selector_type, selector_value in selectors:
                job_cards = self.driver.find_elements(selector_type, selector_value)
                logger.info(f"Using selector '{selector_value}', found {len(job_cards)} job cards")
                if job_cards:
                    break

            if not job_cards:
                logger.warning("No job cards found with any selector.")
                return jobs

            logger.info(f"Found {len(job_cards)} job cards on LinkedIn for {job_title} in {location}")
            max_jobs_to_process = min(10, len(job_cards))  # Limit to 10 jobs for testing

            for idx in range(max_jobs_to_process):
                logger.info(f"Processing job {idx + 1}/{max_jobs_to_process}")
                try:
                    card = job_cards[idx]
                    # Scroll the card into view to avoid interception
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(1)

                    # Try to click using JavaScript to bypass interception
                    try:
                        self.driver.execute_script("arguments[0].click();", card)
                    except Exception as e:
                        logger.warning(f"JavaScript click failed: {e}, skipping this job.")
                        continue

                    time.sleep(3)  # Wait longer for job details to load

                    # Extract job details with updated selectors for title and company
                    try:
                        title_element = WebDriverWait(self.driver, 8).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR,
                                                            "h1.top-card-layout__title, h2.topcard__title, span.job-search-card__title, h2.jobs-unified-top-card__job-title"))
                        )
                        title = title_element.text.strip() if title_element else "Unknown Title"
                    except TimeoutException:
                        title = "Unknown Title"
                        logger.warning("Could not find job title.")

                    try:
                        company_element = self.driver.find_element(By.CSS_SELECTOR,
                                                                   "a.topcard__org-name-link, span.job-search-card__subtitle, div.base-search-card__subtitle, span.jobs-unified-top-card__company-name")
                        company = company_element.text.strip() if company_element else "Unknown Company"
                    except Exception:
                        company = "Unknown Company"
                        logger.warning("Could not find company name.")

                    try:
                        link = card.get_attribute("href") or self.driver.current_url
                    except Exception:
                        link = self.driver.current_url
                        logger.warning("Could not extract job link.")

                    # Extract job description
                    try:
                        description_element = WebDriverWait(self.driver, 8).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR,
                                                            "div.description__text, div.show-more-less-html__markup, section.core-section-container__content, div.jobs-description-content__text"))
                        )
                        description = description_element.text if description_element else ""
                    except TimeoutException:
                        description = ""
                        logger.warning("Could not find job description.")

                    # Extract emails from description
                    emails = EmailExtractor.extract_emails(description)
                    logger.info(f"Found {len(emails)} email(s) for job {idx + 1}: {emails}")

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
                    print(jobs)
                    logger.info(f"Successfully extracted details for job {idx + 1}: {title} at {company}")

                except (ElementClickInterceptedException, ElementNotInteractableException) as e:
                    logger.error(f"Error extracting job details for job {idx + 1}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error extracting job details for job {idx + 1}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")

        return jobs
