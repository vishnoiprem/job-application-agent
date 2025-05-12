from playwright.sync_api import sync_playwright
import json

def load_linkedin_with_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # Load cookies from file
        with open("linkedin_cookies.json", "r") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)

        page = context.new_page()
        page.goto("https://www.linkedin.com/feed/")
        page.wait_for_timeout(5000)

        # Now you're logged in!
        print("✅ Logged in with cookies")

        # Go to jobs
        page.goto("https://www.linkedin.com/jobs/search/?keywords=data+engineer&location=singapore")
        page.wait_for_timeout(10000)

        # Your scraping logic here...

        browser.close()