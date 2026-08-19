from playwright_termux.browser import Chromium
import urllib.parse
import time


html = """
<!doctype html>
<html>
<body>

<div id="container"></div>

<script>
setTimeout(() => {
    const button = document.createElement("button");

    button.id = "delayed";
    button.textContent = "Delayed Button";

    button.onclick = () => {
        document.querySelector("#result").textContent =
            "clicked";
    };

    document.querySelector("#container").appendChild(button);
}, 1000);
</script>

<p id="result"></p>

</body>
</html>
"""


with Chromium(headless=True) as browser:
    page = browser.new_page()

    page.goto(
        "data:text/html,"
        + urllib.parse.quote(html)
    )

    start = time.monotonic()

    page.locator("#delayed").click(timeout=5000)

    elapsed = time.monotonic() - start

    print(
        "Result:",
        page.locator("#result").text_content(),
    )

    print(
        "Waited:",
        round(elapsed, 2),
        "seconds",
    )
