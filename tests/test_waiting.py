from playwright_termux.browser import Chromium
import urllib.parse


html = """
<!doctype html>
<html>
<body>

<div id="result"></div>

<script>
setTimeout(() => {
    document.querySelector("#result").textContent = "Loaded!";
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

    print("Waiting for #result...")

    page.locator("#result").wait_for(
        state="attached"
    )

    page.wait_for_timeout(100)

    print(
        "Result:",
        page.locator("#result").text_content()
    )

    page.wait_for_selector(
        "#result",
        state="visible"
    )

    print("Selector visible: OK")

    page.wait_for_url(
        "data:text/html,*"
    )

    print("URL wait: OK")
