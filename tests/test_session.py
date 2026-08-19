from playwright_termux.browser import Chromium

with Chromium(headless=True) as browser:
    targets = browser.cdp.send("Target.getTargets")["targetInfos"]

    page_target = next(
        target
        for target in targets
        if target["type"] == "page"
    )

    result = browser.cdp.send(
        "Target.attachToTarget",
        {
            "targetId": page_target["targetId"],
            "flatten": True,
        },
    )

    print("TARGET ATTACHED!")
    print("Target:", page_target["targetId"])
    print("Session:", result["sessionId"])
