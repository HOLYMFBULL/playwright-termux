# Playwright-Termux

`playwright-termux` is a specialized Python library designed to bring Playwright-like browser automation to Android environments via Termux. It allows you to control a Chromium browser using the Chrome DevTools Protocol (CDP), bypassing the limitations typically found when trying to run standard Playwright directly on Android/Termux.

## What is it?

Standard Playwright relies on pre-compiled browser binaries (Node.js/C++) that are built for standard Linux distributions (like Ubuntu or Debian). Termux runs a unique environment (built on Android's Bionic libc), meaning standard Playwright binaries often fail to run, or are difficult to patch.

`playwright-termux` solves this by:
1. Connecting directly to Termux's native `chromium-browser` package.
2. Using the Chrome DevTools Protocol (CDP) to drive the browser entirely in Python via WebSockets.
3. Providing an API heavily inspired by Playwright's core primitives (`Browser`, `Page`, `Context`, `Locator`), so your existing Playwright knowledge easily translates.

## How to Integrate and Automate Web Workflows

### Prerequisites

You need Python, Chromium, and (optionally) an X11 setup if you want to see the browser.

```bash
pkg install python chromium-browser
pip install playwright-termux
```

### Basic Usage (Headless)

For background scraping and automation without a display:

```python
from playwright_termux import Chromium

with Chromium(headless=True) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
```

### Advanced Usage (Headed with Termux:X11)

To run automated workflows where you can visually see the browser working, you can use Termux:X11.

1. Install and start `termux-x11`.
2. Export your display variable: `export DISPLAY=:0`
3. Run the script:

```python
from playwright_termux import Chromium

# Will automatically pick up the DISPLAY environment variable
with Chromium(headless=False) as browser:
    page = browser.new_page()
    page.goto("https://github.com")

    # Interact using locators
    search_bar = page.locator("[placeholder='Search GitHub']")
    search_bar.fill("playwright-termux")
    search_bar.press("Enter")

    page.wait_for_timeout(5000) # Wait and observe
```

## Workflows and CI/CD Structure

We strongly believe in clear, maintainable workflows, both for using this tool and for distributing it.

### Publishing to PyPI

We maintain an automated CI/CD workflow to ensure `playwright-termux` is easily installable for end users. Our GitHub Actions workflow (`.github/workflows/publish.yml`) ensures that every time a new release is published on GitHub, the package is built and pushed to PyPI.

How it works:
1. **Trigger:** The workflow listens for the `release: published` event.
2. **Build:** It checks out the code, sets up Python, and uses standard `build` tools to create source distributions and wheels.
3. **Publish:** It uses `pypa/gh-action-pypi-publish` with Trusted Publishing (OIDC) to securely push the new version to PyPI.

This automation allows contributors to focus on improving the library while the build system ensures clean, reproducible, and secure releases.

## Documentation and Examples

- **Docs:** Read more in our `docs/` folder for guides on API usage, locators, context management, and more.
- **Examples:** Check the `examples/` folder for ready-to-run automation scripts for common workflows (forms, cookies, screenshots).
