
from playwright.sync_api import sync_playwright

def verify_contact_link():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the local HTML file
        # Assuming the script runs from repo root
        page.goto("file:///app/index.html")

        # Check Desktop Menu
        # Locate the desktop menu container
        desktop_menu = page.locator(".hidden.md\\:flex")

        # Check if 'Contact' link exists in desktop menu
        contact_link = desktop_menu.get_by_role("link", name="Contact")

        if contact_link.count() > 0:
            print("Contact link found in Desktop Menu")
            href = contact_link.get_attribute("href")
            print(f"Desktop Link HREF: {href}")
        else:
            print("Contact link NOT found in Desktop Menu")

        # Take a screenshot of the header
        page.screenshot(path="verification/header_desktop.png", clip={"x": 0, "y": 0, "width": 1280, "height": 100})

        # Mobile Menu Verification
        # Resize viewport to mobile
        page.set_viewport_size({"width": 375, "height": 812})

        # Click hamburger menu
        page.click("#mobile-menu-btn")

        # Wait for animation/overlay
        page.wait_for_timeout(500)

        # Check if 'Contact' link exists in mobile menu
        mobile_menu = page.locator("#mobile-menu")
        contact_link_mobile = mobile_menu.get_by_role("link", name="Contact")

        if contact_link_mobile.count() > 0:
            print("Contact link found in Mobile Menu")
            href = contact_link_mobile.get_attribute("href")
            print(f"Mobile Link HREF: {href}")
        else:
            print("Contact link NOT found in Mobile Menu")

        # Take a screenshot of the mobile menu
        page.screenshot(path="verification/header_mobile.png")

        browser.close()

if __name__ == "__main__":
    verify_contact_link()
