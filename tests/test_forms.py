from playwright_termux.browser import Chromium
import urllib.parse


html = """
<!doctype html>
<html>
<body>

<label>
    <input type="checkbox" id="terms">
    Accept terms
</label>

<label>
    <input type="radio" name="plan" id="free" value="free">
    Free
</label>

<label>
    <input type="radio" name="plan" id="pro" value="pro">
    Pro
</label>

</body>
</html>
"""


with Chromium(headless=True) as browser:
    page = browser.new_page()

    page.goto(
        "data:text/html,"
        + urllib.parse.quote(html)
    )

    terms = page.locator("#terms")

    print("Initially checked:", terms.is_checked())

    terms.check()

    print("After check:", terms.is_checked())

    terms.uncheck()

    print("After uncheck:", terms.is_checked())

    free = page.locator("#free")
    pro = page.locator("#pro")

    free.check()

    print("Free:", free.is_checked())
    print("Pro:", pro.is_checked())

    pro.check()

    print("Free after Pro:", free.is_checked())
    print("Pro after Pro:", pro.is_checked())
