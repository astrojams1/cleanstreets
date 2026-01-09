from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto('file:///app/index.html')
        page.wait_for_load_state('networkidle')

        # Scroll down to trigger shrink
        page.evaluate("window.scrollTo(0, 100)")
        page.wait_for_timeout(500) # wait for transition

        # Check if classes are applied
        clean_class = page.locator('#logo-clean').get_attribute('class')
        streets_class = page.locator('#logo-streets').get_attribute('class')

        print(f"Clean classes (shrunk): {clean_class}")
        print(f"Streets classes (shrunk): {streets_class}")

        if 'leading-5' not in clean_class:
            print("FAIL: leading-5 missing on Clean (shrunk)")
        if 'leading-3' not in streets_class:
            print("FAIL: leading-3 missing on Streets (shrunk)")

        # Scroll up to trigger expand
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)

        clean_class = page.locator('#logo-clean').get_attribute('class')
        streets_class = page.locator('#logo-streets').get_attribute('class')

        print(f"Clean classes (expanded): {clean_class}")
        print(f"Streets classes (expanded): {streets_class}")

        if 'leading-7' not in clean_class:
            print("FAIL: leading-7 missing on Clean (expanded)")
        if 'leading-5' not in streets_class:
            print("FAIL: leading-5 missing on Streets (expanded)")

        browser.close()

if __name__ == "__main__":
    run()
