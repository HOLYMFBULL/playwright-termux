from playwright_termux.browser import Chromium
import urllib.parse


html = """
<!doctype html>
<html>
<body>

<div id="result">Waiting...</div>

<script>
setTimeout(() => {
    document.querySelector("#result").textContent =
        "Loaded!";
}, 1000);
</script>

</body>
</html>
"""


with Chromium(headless=True) as browser:
    page = browser.new_page()

    page.goto(
        "data:text/html,"
        + urllib.parse.quote(html)
    )

    print("Initial:", page.locator("#result").text_content())

    page.wait_for_function(
        "document.querySelector('#result').textContent === 'Loaded!'"
    )

    print(
        "After wait:",
        page.locator("#result").text_content()
    )

    print("wait_for_function: OK")
