import time
import logging
import json
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from job_application.scrapers.base import JobScraper
from job_application.email_manager import EmailExtractor

logger = logging.getLogger(__name__)


class LinkedInScraper(JobScraper):
    """Scraper for LinkedIn job postings."""

    def scrape_jobs(self, job_title, location):
        if not self.driver:
            self._initialize_driver()

        # ✅ Load cookies
        cookie_path = Path("data/linkedin_cookies.json")
        if cookie_path.exists():
            self.driver.get("https://www.linkedin.com")
            with open(cookie_path) as f:
                cookies = json.load(f)
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"Cookie error: {e}")
            self.driver.refresh()
            logger.info("✅ LinkedIn cookies loaded")
        else:
            logger.warning("⚠️ No cookie file found. Login may be required.")

        jobs = []
        logger.info(f"Searching LinkedIn for {job_title} in {location}")

        formatted_job = job_title.replace(' ', '%20')
        formatted_location = location.replace(' ', '%20')
        url = f"https://www.linkedin.com/jobs/search/?keywords={formatted_job}&location={formatted_location}&f_TPR=r604800"

        try:
            self.driver.get(url)
            time.sleep(8)

            # Scroll page
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            job_cards = self.driver.find_elements(By.CLASS_NAME, "base-card")
            logger.info(f"Found {len(job_cards)} job cards")

            for idx, card in enumerate(job_cards[:10]):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", card)
                    time.sleep(3)

                    # Wait for details panel
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "jobs-details__main-content"))
                    )

                    # ✅ Extract title
                    try:
                        # title_element = WebDriverWait(self.driver, 5).until(
                        #     EC.presence_of_element_located((By.CSS_SELECTOR, "h1.top-card-layout__title, h2.jobs-unified-top-card__job-title"))
                        # )
                        title_element = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "h2.jobs-unified-top-card__job-title"))
                        )

                        title = title_element.text.strip()
                    except Exception:
                        title = "Unknown Title"
                        logger.warning("Could not extract title")

                    # ✅ Extract company
                    try:
                        # company_element = self.driver.find_element(By.CSS_SELECTOR, "a.topcard__org-name-link, span.jobs-unified-top-card__company-name")
                        # company = company_element.text.strip()

                        # company_element = WebDriverWait(self.driver, 10).until(
                        #     EC.presence_of_element_located(
                        #         (By.CSS_SELECTOR, "span.jobs-unified-top-card__company-name"))
                        # )
                        company_element = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-search__job-details"))
                        )
                        company = company_element.text.strip()
                    except Exception:
                        company = "Unknown Company"
                        logger.warning("Could not extract company")

                    # ✅ Extract URL
                    try:
                        link = card.get_attribute("href") or self.driver.current_url
                    except:
                        link = self.driver.current_url

                    # ✅ Extract job description
                    try:
                        description_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.show-more-less-html__markup"))
                        )
                        description = description_element.text.strip()
                    except TimeoutException:
                        description = ""
                        logger.warning("Could not extract description")

                    # ✅ Extract email from description
                    emails = EmailExtractor.extract_emails(description)

                    job_data = {
                        "title": title,
                        "company": company,
                        "location": location,
                        "url": link,
                        "description": description,
                        "emails": emails,
                        "source": "linkedin"
                    }
                    jobs.append(job_data)

                except Exception as e:
                    logger.error(f"❌ Failed to extract job {idx + 1}: {e}")
                    continue

        except Exception as e:
            logger.error(f"🔴 General scraping error: {e}")

        return jobs