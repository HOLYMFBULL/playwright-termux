from pathlib import Path
from playwright_termux.browser import Chromium
import urllib.parse


build = Path("build")
build.mkdir(exist_ok=True)

file1 = build / "upload_one.txt"
file2 = build / "upload_two.txt"

file1.write_text("Hello from Playwright-Termux 2.0")
file2.write_text("Second upload file")


html = """
<!doctype html>
<html>
<body>

<input id="file" type="file" multiple>

<p id="count">0</p>

<script>
const input = document.querySelector("#file");

input.addEventListener("change", () => {
    document.querySelector("#count").textContent =
        input.files.length;
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

    upload = page.locator("#file")

    print("Uploading one file...")

    upload.set_input_files(file1)

    print(
        "Files:",
        page.evaluate(
            "document.querySelector('#file').files.length"
        )
    )

    print("Uploading two files...")

    upload.set_input_files([
        file1,
        file2,
    ])

    print(
        "Files:",
        page.evaluate(
            "document.querySelector('#file').files.length"
        )
    )
