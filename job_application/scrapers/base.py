from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class JobScraper:
    """Base class for job scrapers."""
    
    def __init__(self, config):
        self.config = config
        self.driver = None
        
    def _initialize_driver(self):
        """Initialize the Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    
    def close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def scrape_jobs(self, job_title, location):
        """Scrape jobs for a given title and location."""
        raise NotImplementedError("Subclasses must implement this method")
