from playwright_termux.browser import Chromium

html = """
<!doctype html>
<html>
<head>
    <title>Locator Test</title>
</head>
<body>
    <h1>Hello Termux</h1>
    <p id="message">Playwright-Termux 2.0</p>
</body>
</html>
"""

with Chromium(headless=True) as browser:
    page = browser.new_page()

    import urllib.parse

    url = "data:text/html," + urllib.parse.quote(html)

    page.goto(url)

    print("Title:", page.title())

    result = page.evaluate(
        "document.querySelector('h1').textContent"
    )

    print("H1:", result)
