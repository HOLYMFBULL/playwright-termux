"""
Headed Chromium Example (Requires Termux:X11)

This script demonstrates how to launch Chromium in headed mode so you can
visually watch the automation process.

Prerequisites:
1. Install Termux:X11
2. Start the Termux:X11 app
3. Run this script: `export DISPLAY=:0 && python x11.py`
"""

import os
import time
from playwright_termux import Chromium

def main():
    # Ensure DISPLAY is set for Termux:X11
    if not os.environ.get("DISPLAY"):
        print("WARNING: DISPLAY environment variable not found.")
        print("To run in headed mode, you must set DISPLAY (e.g., export DISPLAY=:0)")
        print("Falling back to headless mode for demonstration purposes...")
        headless_mode = True
    else:
        print(f"Using DISPLAY: {os.environ.get('DISPLAY')}")
        headless_mode = False

    print("Launching Chromium...")
    # headless=False requires an X11 server to render the GUI
    with Chromium(headless=headless_mode) as browser:
        context = browser.new_context()
        page = context.new_page()

        print("Navigating to Wikipedia...")
        page.goto("https://en.wikipedia.org/wiki/Main_Page")

        # Give the user a moment to see the page load
        time.sleep(2)

        print("Typing into the search bar...")
        # Locate the search input and type something
        search_input = page.locator("input[name='search']")
        search_input.fill("Playwright")

        # Give the user a moment to see the typed text
        time.sleep(1)

        print("Submitting search...")
        # Press the Enter key to submit the form
        search_input.press("Enter")

        # Wait for the results page to load
        page.wait_for_timeout(3000)

        print(f"Landed on: {page.title()}")

        print("Closing in 3 seconds...")
        time.sleep(3)

if __name__ == "__main__":
    main()
