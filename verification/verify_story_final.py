
from playwright.sync_api import sync_playwright

def verify_story_changes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the local HTML file
        page.goto("file:///app/index.html")

        # Hide the sticky header to avoid it blocking the view in the screenshot
        page.evaluate("document.querySelector('nav').style.display = 'none'")

        # Locate the story section
        story_section = page.locator("#story")

        # Ensure it's visible
        story_section.wait_for(state="visible")

        # Take a screenshot of the specific element
        story_section.screenshot(path="verification/final_story_verification.png")

        browser.close()

if __name__ == "__main__":
    verify_story_changes()
