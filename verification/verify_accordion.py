from playwright.sync_api import sync_playwright

def verify_accordion_accessibility():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the local index.html using the file protocol
        # Note: In this environment, the path is /app/index.html
        page.goto("file:///app/index.html")

        # Locate the first accordion button
        btn = page.locator("#faq-btn-start")

        # Check initial attributes
        expanded = btn.get_attribute("aria-expanded")
        controls = btn.get_attribute("aria-controls")
        print(f"Initial state: aria-expanded={expanded}, aria-controls={controls}")

        if expanded != "false":
            print("FAIL: Initial aria-expanded should be false")

        if controls != "faq-answer-start":
             print("FAIL: aria-controls incorrect")

        # Scroll to FAQ section to make sure it's in view for screenshot
        btn.scroll_into_view_if_needed()

        # Take a screenshot before interaction
        page.screenshot(path="verification/before_interaction.png")

        # Click the button
        print("Clicking accordion button...")
        btn.click()

        # Wait for potential animation/state change
        page.wait_for_timeout(500)

        # Check attributes after click
        new_expanded = btn.get_attribute("aria-expanded")
        print(f"After click: aria-expanded={new_expanded}")

        if new_expanded != "true":
            print("FAIL: aria-expanded should be true after click")

        # Check if content is visible (class 'active' or opacity)
        content = page.locator("#faq-answer-start")
        is_visible = content.is_visible()
        class_attr = content.get_attribute("class")
        print(f"Content visibility: {is_visible}, Classes: {class_attr}")

        # Take a screenshot after interaction (shows open state)
        page.screenshot(path="verification/after_interaction.png")

        # Focus state check
        # We simulate Tab navigation to the button
        # Reload page to reset focus
        page.reload()
        page.keyboard.press("Tab") # Logo Clean
        page.keyboard.press("Tab") # Logo Streets
        # ... tabbing might take a while to get to FAQ.
        # Let's just focus directly and check screenshot for ring
        btn.focus()
        page.screenshot(path="verification/focus_state.png")
        print("Focus state screenshot taken.")

        browser.close()

if __name__ == "__main__":
    verify_accordion_accessibility()
