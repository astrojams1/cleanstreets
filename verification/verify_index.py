from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8000/index.html")

        # Wait for the supporters to be visible
        page.wait_for_selector("#supporters-list")

        # Take a screenshot
        page.screenshot(path="verification/index_full.png", full_page=True)

        # Also screenshot the "years operating" part to be sure
        element = page.locator("#story")
        element.screenshot(path="verification/story_section.png")

        browser.close()

if __name__ == "__main__":
    run()
