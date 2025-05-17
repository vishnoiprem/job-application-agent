import logging
import time
import re
import pandas as pd
import configparser
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ——— DEBUG Logging Setup ———
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("webdriver_manager").setLevel(logging.DEBUG)

# ——— Load config.ini ———
config = configparser.ConfigParser()
config.read("config.ini")
try:
    EMAIL        = config.get("LinkedIn", "EMAIL")
    PASSWORD     = config.get("LinkedIn", "PASSWORD")
    CSV_FILENAME = config.get("Output", "CSV_FILENAME")
except (configparser.NoSectionError, configparser.NoOptionError) as e:
    logging.error(f"Configuration error: {e}")
    raise SystemExit("Please ensure config.ini exists with [LinkedIn] EMAIL, PASSWORD and [Output] CSV_FILENAME")

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--enable-logging")
    options.add_argument("--v=1")

    service = Service(
        ChromeDriverManager().install(),
        log_path="chromedriver.log"
    )
    return webdriver.Chrome(service=service, options=options)

def linkedin_login(driver, email, password):
    logging.info("Navigating to LinkedIn login page")
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(email)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
    WebDriverWait(driver, 10).until(EC.url_contains("/feed/"))
    logging.info("Login successful!")

def search_jobs(driver, search_query, location, days):
    seconds = days * 86400
    q   = urllib.parse.quote(search_query)
    loc = urllib.parse.quote(location)
    url = f"https://www.linkedin.com/jobs/search/?keywords={q}&location={loc}&f_TPR=r{seconds}"
    logging.info(f"Loading job search URL: {url}")
    driver.get(url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.jobs-search__results-list li"))
    )

def scroll_job_listings(driver, scroll_pause=2, max_scrolls=10):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(max_scrolls):
        logging.debug(f"Scrolling window, iteration {i+1}/{max_scrolls}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            logging.debug("No further page height increase; assuming end.")
            break
        last_height = new_height

def extract_job_details(driver):
    # 1) collect all job-card links
    cards = driver.find_elements(By.CSS_SELECTOR, "a.base-card__full-link")
    links = [c.get_attribute('href') for c in cards]
    logging.info(f"Found {len(links)} job links to scrape")

    data = []
    home = driver.current_window_handle

    for idx, link in enumerate(links, start=1):
        logging.debug(f"[{idx}/{len(links)}] Opening: {link}")
        # open detail in new tab
        driver.execute_script("window.open(arguments[0]);", link)
        driver.switch_to.window(driver.window_handles[-1])

        try:
            # wait for detail page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-unified-top-card__job-title"))
            )

            title_el   = driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__job-title")
            company_el = driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__company-name")
            desc_el    = driver.find_element(By.CLASS_NAME, "jobs-description__content")

            title   = title_el.text.strip()
            company = company_el.text.strip()
            desc    = desc_el.text.strip()

            # skills might not always be present
            skills_els = driver.find_elements(
                By.XPATH, "//span[contains(@class,'job-details-skill-match-status__skill')]"
            )
            skills = [s.text for s in skills_els]

            # look for email in description
            email = "Not found"
            for m in re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', desc):
                email = m
                break

            data.append({
                "Title": title,
                "Company": company,
                "Description": desc,
                "Skills": ", ".join(skills),
                "Email": email,
                "Link": link
            })
            logging.debug(f"Scraped: {title} @ {company}")

        except Exception as e:
            logging.error(f"Failed scraping {link}: {e}")

        # close tab and switch back
        driver.close()
        driver.switch_to.window(home)
        time.sleep(1)

    return data

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    logging.info(f"Saved {len(data)} records to {filename}")

def main():
    driver = initialize_driver()
    try:
        linkedin_login(driver, EMAIL, PASSWORD)

        # you can hard-code or prompt these:
        search_query = input("Job keyword (e.g. data engineer): ").strip()
        location     = input("Location (e.g. Bangkok): ").strip()
        days_posted  = int(input("Posted within last how many days? ").strip())

        search_query = "data engineer"
        location     = "Singapore"
        days_posted  =1


        search_jobs(driver, search_query, location, days_posted)
        scroll_job_listings(driver)
        results = extract_job_details(driver)
        save_to_csv(results, CSV_FILENAME)

    except Exception as e:
        logging.error(f"Fatal error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
