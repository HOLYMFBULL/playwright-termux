
from playwright_termux import Chromium


def test_page_api():
    with Chromium(headless=True) as browser:
        page = browser.new_page()

        page.goto("https://example.com")

        assert page.title() == "Example Domain"
        assert page.url == "https://example.com/"

        assert page.locator("h1").count() == 1
        assert page.locator("h1").text_content() == "Example Domain"

        assert page.content()
        assert page.evaluate("1 + 2") == 3

        page.reload()

        assert page.url == "https://example.com/"

        page.close()


def test_navigation_api():
    with Chromium(headless=True) as browser:
        page = browser.new_page()

        page.goto("https://example.com")
        page.goto("https://example.org")

        page.go_back()
        assert page.url == "https://example.com/"

        page.go_forward()
        assert page.url == "https://example.org/"

        page.close()


def test_network_api():
    with Chromium(headless=True) as browser:
        page = browser.new_page()

        requests = []
        responses = []

        page.network.on_request(
            lambda request: requests.append(request)
        )

        page.network.on_response(
            lambda response: responses.append(response)
        )

        page.goto("https://example.com")

        assert requests
        assert responses

        page.close()


def test_context_api():
    with Chromium(headless=True) as browser:
        context = browser.new_context()

        page = context.new_page()

        page.goto("https://example.com")

        context.add_cookies([
            {
                "name": "test_cookie",
                "value": "works",
                "url": "https://example.com/",
            }
        ])

        cookies = context.cookies()

        assert any(
            c["name"] == "test_cookie"
            for c in cookies
        )

        assert not context.is_closed

        context.close()

        assert context.is_closed
