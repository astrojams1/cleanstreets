
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Load local index.html
        page.goto("file:///app/index.html")

        # Hide the sticky header to see content better
        page.evaluate("document.querySelector('nav').style.display = 'none'")

        # Scroll to impact section
        page.locator("#impact").scroll_into_view_if_needed()

        # Take screenshot of the impact section
        # We can locate the h2 directly
        impact_header = page.locator("#impact h2")
        impact_header.screenshot(path="verification/impact_header.png")

        browser.close()

if __name__ == "__main__":
    run()
