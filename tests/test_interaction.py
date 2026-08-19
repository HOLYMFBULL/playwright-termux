from playwright_termux.browser import Chromium
import urllib.parse


html = """
<!doctype html>
<html>
<head>
    <title>Interaction Test</title>
</head>
<body>

<input id="name" type="text">

<button id="submit">Submit</button>

<p id="output"></p>

<script>
document.querySelector("#submit").addEventListener("click", () => {
    document.querySelector("#output").textContent =
        document.querySelector("#name").value;
});

document.querySelector("#name").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        document.querySelector("#output").textContent =
            document.querySelector("#name").value;
    }
});
</script>

</body>
</html>
"""


with Chromium(headless=True) as browser:
    page = browser.new_page()

    url = "data:text/html," + urllib.parse.quote(html)

    page.goto(url)

    name = page.locator("#name")
    submit = page.locator("#submit")
    output = page.locator("#output")

    print("Filling...")
    name.fill("Mastro")

    print(
        "Input value:",
        page.evaluate(
            "document.querySelector('#name').value"
        ),
    )

    print("Clicking...")
    submit.click()

    print(
        "After click:",
        output.text_content(),
    )

    print("Testing Enter...")
    name.fill("Termux")

    name.press("Enter")

    print(
        "After Enter:",
        output.text_content(),
    )
