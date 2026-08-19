from playwright_termux.browser import Chromium


def test_page_basic():
    with Chromium(headless=True) as browser:
        page = browser.new_page()

        page.goto("https://example.com")

        assert page.url == "https://example.com/"
        assert page.title() == "Example Domain"
        assert page.evaluate("1 + 2") == 3

        page.close()
