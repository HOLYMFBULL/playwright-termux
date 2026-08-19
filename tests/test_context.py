from playwright_termux.browser import Chromium


def test_browser_contexts():
    with Chromium(headless=True) as browser:
        context1 = browser.new_context()
        context2 = browser.new_context()

        page1 = context1.new_page()
        page2 = context2.new_page()

        page1.goto("data:text/html,<title>Context One</title>")
        page2.goto("data:text/html,<title>Context Two</title>")

        assert page1.title() == "Context One"
        assert page2.title() == "Context Two"

        assert page1.context is not page2.context

        context1.close()
        context2.close()
