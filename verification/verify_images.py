from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the local HTML file
        page.goto(f"file://{os.getcwd()}/index.html")

        # Take screenshot of the Hero section (top)
        page.screenshot(path="verification/hero_image.png", clip={"x": 0, "y": 0, "width": 1280, "height": 800})

        # Take screenshot of the Story section (bottom) where the second image is
        # We scroll to the element to ensure it is visible and lazy loaded
        story_img = page.locator("#press img").first # The story image is in the section just before or inside press/story
        # Actually based on index.html inspection, the bottom image is likely near the #our-story or similar section.
        # Let's target the images by src to be precise.

        page.locator('img[src="images/worker.png"]').scroll_into_view_if_needed()
        page.locator('img[src="images/working.png"]').scroll_into_view_if_needed()

        # Wait a bit for lazy loading
        page.wait_for_timeout(1000)

        # Screenshot specifically the working.png image area
        page.locator('img[src="images/working.png"]').screenshot(path="verification/story_image.png")

        browser.close()

if __name__ == "__main__":
    run()
