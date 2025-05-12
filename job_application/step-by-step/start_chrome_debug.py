from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

# Set up Chrome options to connect to existing session
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")

print("Connecting to existing Chrome session...")
try:
    driver = webdriver.Chrome(options=chrome_options)
    print("Connected successfully!")
except Exception as e:
    print("Failed to connect:", e)
    exit()

# Open a new tab
driver.execute_script("window.open('');")
time.sleep(1)

# Switch to the new tab
driver.switch_to.window(driver.window_handles[-1])

# Navigate to LinkedIn Jobs
print("Opening LinkedIn Jobs page...")
driver.get("https://www.linkedin.com/jobs ")
time.sleep(3)

# Optional: Do some actions here like login or search jobs
# For now, just print title
print("Page Title:", driver.title)

# Example: Search for Data Analyst in Singapore
search_box = driver.find_element("xpath", '//input[@aria-label="Search by title, skill, or company"]')
search_box.send_keys("Data Analyst")
search_box.send_keys(Keys.RETURN)

time.sleep(5)

print("Automation complete.")