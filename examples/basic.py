"""
Basic Headless Web Scraping Example

This script demonstrates how to launch Chromium in headless mode,
navigate to a website, extract information, and take a screenshot.
"""

from playwright_termux import Chromium
import time

def main():
    print("Launching headless Chromium...")
    # headless=True is perfect for background tasks or running without an X11 server
    with Chromium(headless=True) as browser:
        # Create an isolated context
        context = browser.new_context()

        # Create a new page/tab
        page = context.new_page()

        url = "https://example.com"
        print(f"Navigating to {url}...")
        page.goto(url)

        # Wait for network idle or a specific element if necessary,
        # but locators automatically wait!

        # Extract the page title
        title = page.title()
        print(f"\n[+] Extracted Title: '{title}'")

        # Find the main heading using a CSS locator
        heading = page.locator("h1").inner_text()
        print(f"[+] Extracted Heading: '{heading}'")

        # Find the first paragraph
        paragraph = page.locator("p").first.inner_text()
        print(f"[+] Extracted Paragraph:\n    {paragraph}")

        print("\nAll tasks completed successfully. Closing browser.")

if __name__ == "__main__":
    main()
