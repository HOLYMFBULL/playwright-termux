# Getting Started with Playwright-Termux

`playwright-termux` is designed to be intuitive and similar to the official Playwright Python API, but optimized for the limitations and architecture of Termux on Android.

## Writing Your First Script

Let's write a simple script that opens a website, extracts the title, and takes a screenshot.

Create a file named `scrape.py` and add the following:

```python
from playwright_termux import Chromium

# Launch the Chromium browser in headless mode
with Chromium(headless=True) as browser:
    # Create a new browser context (similar to an incognito window)
    context = browser.new_context()

    # Open a new tab/page within that context
    page = context.new_page()

    print("Navigating to example.com...")
    page.goto("https://example.com")

    # Extract the title
    title = page.title()
    print(f"Page title is: {title}")

    # Find an element using a CSS locator and extract its text
    heading = page.locator("h1").inner_text()
    print(f"Page heading is: {heading}")
```

Run this script in your Termux terminal:
```bash
python scrape.py
```

## Basic Concepts

### 1. The Browser (Chromium)

The `Chromium` class is the main entry point. It handles launching the Termux `chromium-browser` executable and establishing a connection over the Chrome DevTools Protocol (CDP).

Using a `with` statement ensures the browser process and any temporary user data directories are properly cleaned up when your script finishes.

### 2. Browser Contexts

A Context (`browser.new_context()`) is an isolated session. Cookies, local storage, and other browsing data are separate from other contexts. This is incredibly useful for simulating multiple independent users or isolating tests.

### 3. Pages

A Page (`context.new_page()`) is a single tab or window within a context. Most of your interactions (navigation, clicking, typing) will happen on the Page object.

### 4. Locators

Locators are the standard way to find elements on the page. Unlike simple DOM selectors that run once, Playwright locators are strict and auto-waiting. When you perform an action (like `.click()`) on a locator, it will automatically wait for the element to appear, become visible, and become interactive.

```python
# Find an input field and type into it
page.locator("input[name='q']").fill("Termux")

# Find a button with specific text and click it
page.locator("text=Search").click()
```

## Next Steps

Now that you know the basics, explore the following documentation pages:
- [Locators](locators.md): Deep dive into element selection.
- [Interactions](interactions.md): Learn how to click, type, and scroll.
- [Headless vs Headed](headless.md): Learn about running scripts visually using Termux:X11.
