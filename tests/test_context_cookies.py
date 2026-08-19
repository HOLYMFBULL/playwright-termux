from playwright_termux.browser import Chromium


def test_context_cookies():
    with Chromium(headless=True) as browser:
        context1 = browser.new_context()
        context2 = browser.new_context()

        page1 = context1.new_page()
        page2 = context2.new_page()

        page1.goto("https://example.com")
        page2.goto("https://example.com")

        context1.add_cookies([
            {
                "name": "user",
                "value": "Mastro",
                "url": "https://example.com/",
            }
        ])

        cookies1 = context1.cookies()
        cookies2 = context2.cookies()

        cookie1 = next(
            (c for c in cookies1 if c["name"] == "user"),
            None,
        )

        cookie2 = next(
            (c for c in cookies2 if c["name"] == "user"),
            None,
        )

        assert cookie1 is not None
        assert cookie1["value"] == "Mastro"

        # Contexts must remain isolated.
        assert cookie2 is None

        context1.clear_cookies()

        cookies1_after = context1.cookies()

        cookie1_after = next(
            (c for c in cookies1_after if c["name"] == "user"),
            None,
        )

        assert cookie1_after is None

        context1.close()
        context2.close()
