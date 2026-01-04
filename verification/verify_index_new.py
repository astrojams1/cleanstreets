from playwright.sync_api import sync_playwright

def verify_index():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8080/index.html")

        # Take a full page screenshot
        page.screenshot(path="verification/index_final_full.png", full_page=True)

        # Take a screenshot of the supporters section specifically
        supporters_section = page.locator("#supporters")
        supporters_section.screenshot(path="verification/index_final_supporters.png")

        browser.close()

if __name__ == "__main__":
    verify_index()
