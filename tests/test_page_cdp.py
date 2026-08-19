import threading

from playwright_termux.browser import Chromium


with Chromium(headless=True) as browser:
    targets = browser.cdp.send("Target.getTargets")["targetInfos"]

    target = next(
        t for t in targets
        if t["type"] == "page"
    )

    session = browser.cdp.create_session(
        target["targetId"]
    )

    session.send("Page.enable")
    session.send("Runtime.enable")
    session.send(
        "Page.setLifecycleEventsEnabled",
        {"enabled": True},
    )

    loaded = threading.Event()
    navigation_loader = {"id": None}

    def on_lifecycle(params):
        if (
            params.get("name") == "load"
            and params.get("loaderId")
            == navigation_loader["id"]
        ):
            print("NAVIGATION LOAD EVENT")
            loaded.set()

    session.on(
        "Page.lifecycleEvent",
        on_lifecycle,
    )

    navigation = session.send(
        "Page.navigate",
        {"url": "https://example.com"},
    )

    navigation_loader["id"] = navigation.get("loaderId")

    if not loaded.wait(15):
        raise RuntimeError(
            "Timed out waiting for navigation"
        )

    url = session.send(
        "Runtime.evaluate",
        {
            "expression": "location.href",
            "returnByValue": True,
        },
    )

    title = session.send(
        "Runtime.evaluate",
        {
            "expression": "document.title",
            "returnByValue": True,
        },
    )

    print("URL:", url["result"].get("value"))
    print("Title:", title["result"].get("value"))

    session.off(
        "Page.lifecycleEvent",
        on_lifecycle,
    )
