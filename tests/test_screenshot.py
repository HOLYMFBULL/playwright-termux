from playwright_termux.browser import Chromium
import urllib.parse


html = """
<!doctype html>
<html>
<body>
    <h1>Playwright-Termux 2.0</h1>
    <p>CDP screenshot test</p>
</body>
</html>
"""


with Chromium(headless=True) as browser:
    page = browser.new_page()

    page.goto(
        "data:text/html,"
        + urllib.parse.quote(html)
    )

    data = page.screenshot(
        "build/test.png"
    )

    print("Screenshot bytes:", len(data))

    import os

    print(
        "File exists:",
        os.path.exists("build/test.png"),
    )
