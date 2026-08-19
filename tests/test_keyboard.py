from playwright_termux.browser import Chromium
import urllib.parse


html = """
<!doctype html>
<html>
<body>

<input id="name">
<p id="result"></p>

<script>
const input = document.querySelector("#name");

input.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        document.querySelector("#result")
            .textContent = "ENTER";
    }
});
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

    page.locator("#name").click()

    page.keyboard.type("Mastro")

    print(
        "Value:",
        page.evaluate(
            "document.querySelector('#name').value"
        ),
    )

    page.keyboard.press("Enter")

    print(
        "Result:",
        page.locator("#result").text_content(),
    )
