from playwright_termux import (
    Chromium,
    BrowserContext,
    Page,
    Locator,
    Network,
    Frame,
    Dialog,
)


def test_public_api():
    assert Chromium is not None
    assert BrowserContext is not None
    assert Page is not None
    assert Locator is not None
    assert Network is not None
    assert Frame is not None
    assert Dialog is not None


def test_browser_page():
    with Chromium(headless=True) as browser:
        page = browser.new_page()

        page.goto("https://example.com")

        assert page.url == "https://example.com/"
        assert page.title() == "Example Domain"
        assert page.evaluate("1 + 2") == 3

        page.reload()

        assert page.url == "https://example.com/"

        page.close()


def test_context_isolation():
    with Chromium(headless=True) as browser:
        context1 = browser.new_context()
        context2 = browser.new_context()

        assert not context1.is_closed
        assert not context2.is_closed
        assert context1 is not context2

        page1 = context1.new_page()
        page2 = context2.new_page()

        page1.goto("https://example.com")
        page2.goto("https://example.org")

        assert page1.url == "https://example.com/"
        assert page2.url == "https://example.org/"

        context1.close()

        assert context1.is_closed
        assert not context2.is_closed

        context2.close()


def test_navigation():
    with Chromium(headless=True) as browser:
        page = browser.new_page()

        page.goto("https://example.com")
        page.goto("https://example.org")

        assert page.url == "https://example.org/"

        page.go_back()
        assert page.url == "https://example.com/"

        page.go_forward()
        assert page.url == "https://example.org/"

        page.close()


def test_page_helpers():
    with Chromium(headless=True) as browser:
        page = browser.new_page()

        page.goto("https://example.com")

        assert page.evaluate("document.readyState") == "complete"

        page.close()
