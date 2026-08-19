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

    heading = page.locator("h1")
    message = page.locator("#message")

    print("H1 count:", heading.count())
    print("H1 text:", heading.text_content())

    print(
        "Message:",
        message.text_content(),
    )

    print(
        "Message ID:",
        message.get_attribute("id"),
    )
