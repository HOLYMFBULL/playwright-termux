from playwright_termux.browser import Chromium
import urllib.parse


html = """
<!doctype html>
<html>
<body>

<select id="country">
    <option value="us">United States</option>
    <option value="in">India</option>
    <option value="jp">Japan</option>
</select>

</body>
</html>
"""


with Chromium(headless=True) as browser:
    page = browser.new_page()

    page.goto(
        "data:text/html,"
        + urllib.parse.quote(html)
    )

    country = page.locator("#country")

    print(
        "Initial:",
        country.input_value()
    )

    country.select_option("in")

    print(
        "By value:",
        country.input_value()
    )

    country.select_option(label="Japan")

    print(
        "By label:",
        country.input_value()
    )

    country.select_option(index=0)

    print(
        "By index:",
        country.input_value()
    )
