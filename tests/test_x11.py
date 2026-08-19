import os
import time
import pytest

from playwright_termux import Chromium


@pytest.mark.x11
def test_headed_x11():
    display = os.environ.get("DISPLAY")

    if not display:
        pytest.skip("DISPLAY is not set")

    browser = Chromium(headless=False)

    try:
        browser.launch()

        page = browser.new_page()
        page.goto("https://example.com")

        assert page.url == "https://example.com/"
        assert page.title() == "Example Domain"

        screenshot = os.path.join(
            os.environ["TMPDIR"],
            "playwright-termux-x11-test.png",
        )

        page.screenshot(screenshot)

        assert os.path.exists(screenshot)
        assert os.path.getsize(screenshot) > 0

        print("X11 DISPLAY:", display)
        print("X11 SCREENSHOT:", screenshot)
        print("X11 HEADED TEST PASSED")

    finally:
        browser.close()
