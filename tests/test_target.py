from playwright_termux.browser import Chromium

with Chromium(headless=True) as browser:
    result = browser.cdp.send("Target.getTargets")

    print("TARGETS:")
    for target in result["targetInfos"]:
        print(
            target.get("type"),
            target.get("url"),
            target.get("targetId"),
        )
