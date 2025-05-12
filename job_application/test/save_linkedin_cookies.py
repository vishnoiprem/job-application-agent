from playwright.sync_api import sync_playwright
import json


def save_linkedin_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Go to LinkedIn login page
        page.goto("https://www.linkedin.com/login")

        print("🟡 Please log in manually...")
        page.wait_for_timeout(30000)  # Wait 30 sec for manual login (or increase time)

        # Save cookies after login
        cookies = context.cookies()
        with open("linkedin_cookies.json", "w") as f:
            json.dump(cookies, f)
        print("✅ Cookies saved to linkedin_cookies.json")

        browser.close()