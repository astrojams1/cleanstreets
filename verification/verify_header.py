from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})

        # Load local index.html
        page.goto('file:///app/index.html')

        # Wait for fonts and content
        page.wait_for_load_state('networkidle')

        # Take a screenshot of the header
        # The header is inside <nav> tag.
        # But let's take a screenshot of the top area including the header and hero
        page.screenshot(path='/app/verification/header_before.png', clip={'x': 0, 'y': 0, 'width': 1280, 'height': 300})

        browser.close()

if __name__ == "__main__":
    run()
