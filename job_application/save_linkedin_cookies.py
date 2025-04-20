from playwright.sync_api import sync_playwright
import json
import os

cookie_path = os.path.join("data", "linkedin_cookies.json")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.linkedin.com/login")
    input("🔐 Please log in to LinkedIn manually, then press Enter to continue...")
    cookies = page.context.cookies()

    os.makedirs("data", exist_ok=True)
    with open(cookie_path, "w") as f:
        json.dump(cookies, f)

    print(f"✅ Cookies saved to {cookie_path}")
    browser.close()