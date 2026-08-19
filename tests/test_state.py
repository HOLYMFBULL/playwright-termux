from playwright_termux.browser import Chromium
import urllib.parse


html = """
<!doctype html>
<html>
<body>

<button id="enabled">Enabled</button>
<button id="disabled" disabled>Disabled</button>

<div id="hidden" style="display:none">
    Hidden
</div>

</body>
</html>
"""


with Chromium(headless=True) as browser:
    page = browser.new_page()

    page.goto(
        "data:text/html,"
        + urllib.parse.quote(html)
    )

    print(
        "Enabled visible:",
        page.locator("#enabled").is_visible(),
    )

    print(
        "Enabled enabled:",
        page.locator("#enabled").is_enabled(),
    )

    print(
        "Disabled enabled:",
        page.locator("#disabled").is_enabled(),
    )

    print(
        "Hidden visible:",
        page.locator("#hidden").is_visible(),
    )
