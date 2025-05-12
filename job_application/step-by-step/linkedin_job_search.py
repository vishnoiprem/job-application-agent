from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def connect_to_chrome():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    print("Connecting to existing Chrome session...")
    driver = webdriver.Chrome(options=chrome_options)
    print("Connected!")
    return driver

def linkedin_job_search(driver, location="Singapore", keyword="Data Analyst", days_old=1):
    driver.get("https://www.linkedin.com/jobs ")
    time.sleep(5)

    try:
        # Wait for search box
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search by title, skill, or company"]'))
        )
        search_box.send_keys(keyword)

        location_box = driver.find_element(By.XPATH, '//input[@aria-label="City, state, or zip code"]')
        location_box.clear()
        location_box.send_keys(location)

        search_button = driver.find_element(By.XPATH, '//button[@aria-label="Search jobs"]')
        search_button.click()

        # Date filter
        if days_old:
            driver.find_element(By.XPATH, '//button[@aria-label="Date posted"]').click()
            time.sleep(1)

            if days_old <= 1:
                driver.find_element(By.XPATH, '//span[text()="Past 24 hours"]').click()
            elif days_old <= 7:
                driver.find_element(By.XPATH, '//span[text()="Past week"]').click()
            elif days_old <= 30:
                driver.find_element(By.XPATH, '//span[text()="Past month"]').click()
            else:
                driver.find_element(By.XPATH, '//span[text()="All time"]').click()

            time.sleep(2)

        # Extract jobs
        jobs = driver.find_elements(By.CLASS_NAME, 'base-search-card__info')
        print(f"\nFound {len(jobs)} jobs:\n")
        for job in jobs[:10]:
            try:
                title = job.find_element(By.CLASS_NAME, 'base-search-card__title').text
                company = job.find_element(By.CLASS_NAME, 'base-search-card__subtitle').text
                print(f"{title} at {company}")
            except Exception as e:
                continue

    except Exception as e:
        print("Error during job search:", e)

if __name__ == "__main__":
    # Step 1: Start Chrome in debug mode
    import start_chrome_debug
    start_chrome_debug.start_chrome_debug()

    # Step 2: Connect and search jobs
    driver = connect_to_chrome()
    linkedin_job_search(driver, location="Singapore", keyword="Data Analyst", days_old=1)