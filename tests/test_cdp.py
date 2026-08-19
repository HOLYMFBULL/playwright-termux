from playwright_termux.browser import Chromium

with Chromium(headless=True) as browser:
    result = browser.cdp.send("Browser.getVersion")
    print("CDP CONNECTED!")
    print("Browser:", result.get("product"))
    print("Protocol:", result.get("protocolVersion"))
