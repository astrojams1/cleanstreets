from playwright.sync_api import sync_playwright

def verify_drop_cap():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Since this is a static site and index.html is in root, we can load it directly
        page.goto("file:///app/index.html")

        # Scroll to the Our Story section where the drop cap is
        # The section id is #story
        story_section = page.locator("#story")
        story_section.scroll_into_view_if_needed()

        # Take a screenshot of the paragraph with the drop cap
        drop_cap_paragraph = page.locator(".drop-cap")
        drop_cap_paragraph.screenshot(path="verification/drop_cap.png")

        browser.close()

if __name__ == "__main__":
    verify_drop_cap()
