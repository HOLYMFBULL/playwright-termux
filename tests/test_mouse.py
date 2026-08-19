from playwright_termux.browser import Chromium
import urllib.parse


html = """
<!doctype html>
<html>
<body style="height:2000px">

<button id="btn"
        style="margin-top:100px">
    Click Me
</button>

<p id="result"></p>

<script>
document.querySelector("#btn").addEventListener(
    "click",
    () => {
        document.querySelector("#result")
            .textContent = "clicked";
    }
);
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

    button = page.locator("#btn")

    button.scroll_into_view_if_needed()

    node_id = button._resolve_node()
    x, y = button._get_center(node_id)

    print("Button:", x, y)

    page.mouse.move(x, y)
    page.mouse.click(x, y)

    print(
        "Result:",
        page.locator("#result").text_content(),
    )

    page.mouse.wheel(0, 500)

    print("Wheel: OK")
