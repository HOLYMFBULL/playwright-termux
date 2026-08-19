import base64
import json
import threading
import time

from .locator import Locator
from .mouse import Mouse
from .keyboard import Keyboard


class Page:
    def __init__(self, browser, session):
        self.browser = browser
        self.context = getattr(
            browser,
            "context",
            None,
        )
        self.session = session
        self.mouse = Mouse(self)
        self.keyboard = Keyboard(self)
        self._url = "about:blank"

        self.session.send("Page.enable")
        self.session.send("Runtime.enable")
        self.session.send(
            "Page.setLifecycleEventsEnabled",
            {"enabled": True},
        )

    @property
    def url(self):
        return self._url

    def _wait_for_navigation(self, timeout=30, expected_url=None):
        """Wait for navigation to settle."""
        deadline = time.monotonic() + timeout

        while True:
            try:
                current_url = self.evaluate("location.href")
                ready_state = self.evaluate("document.readyState")

                if ready_state == "complete":
                    if expected_url is None or current_url == expected_url:
                        self._url = current_url
                        return self

            except Exception:
                pass

            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Navigation timed out after {timeout}s"
                )

            time.sleep(0.05)

    def goto(self, url, timeout=30):
        """Navigate to a URL and wait for the document to load."""
        if not url:
            raise ValueError("url must not be empty")

        loaded = threading.Event()
        navigation_loader = {"id": None}

        def on_lifecycle(params):
            if (
                params.get("name") == "load"
                and params.get("loaderId")
                == navigation_loader["id"]
            ):
                loaded.set()

        self.session.on(
            "Page.lifecycleEvent",
            on_lifecycle,
        )

        try:
            navigation = self.session.send(
                "Page.navigate",
                {"url": url},
            )

            navigation_loader["id"] = navigation.get("loaderId")

            if navigation.get("errorText"):
                raise RuntimeError(
                    f"Navigation failed: {navigation['errorText']}"
                )

            # Some navigations don't provide a loaderId.
            # Fall back to polling document state.
            if navigation_loader["id"]:
                if not loaded.wait(timeout):
                    return self._wait_for_navigation(
                        timeout=timeout,
                        expected_url=url,
                    )
            else:
                return self._wait_for_navigation(
                    timeout=timeout,
                    expected_url=url,
                )

            self._url = self.evaluate("location.href")
            return self

        finally:
            self.session.off(
                "Page.lifecycleEvent",
                on_lifecycle,
            )

    def reload(self, timeout=30):
        """Reload the current page."""
        current_url = self.evaluate("location.href")

        if not current_url or current_url == "about:blank":
            raise RuntimeError("Cannot reload an empty page")

        self.session.send("Page.reload", {
            "ignoreCache": False,
        })

        return self._wait_for_navigation(timeout)

    def go_back(self, timeout=30):
        """Navigate to the previous browser history entry."""
        history = self.session.send(
            "Page.getNavigationHistory"
        )

        entries = history.get("entries", [])
        current_index = history.get("currentIndex", -1)

        if current_index <= 0:
            return None

        target_url = entries[current_index - 1].get("url")

        self.session.send(
            "Page.navigateToHistoryEntry",
            {
                "entryId": entries[current_index - 1]["id"],
            },
        )

        return self._wait_for_navigation(
            timeout=timeout,
            expected_url=target_url,
        )

    def go_forward(self, timeout=30):
        """Navigate to the next browser history entry."""
        history = self.session.send(
            "Page.getNavigationHistory"
        )

        entries = history.get("entries", [])
        current_index = history.get("currentIndex", -1)

        if (
            current_index < 0
            or current_index >= len(entries) - 1
        ):
            return None

        target_url = entries[current_index + 1].get("url")

        self.session.send(
            "Page.navigateToHistoryEntry",
            {
                "entryId": entries[current_index + 1]["id"],
            },
        )

        return self._wait_for_navigation(
            timeout=timeout,
            expected_url=target_url,
        )

    def locator(self, selector):
        return Locator(self, selector)

    def evaluate(self, expression):
        result = self.session.send(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True,
            },
        )

        if "exceptionDetails" in result:
            details = result["exceptionDetails"]

            raise RuntimeError(
                details.get(
                    "text",
                    "JavaScript evaluation failed",
                )
            )

        return result.get(
            "result",
            {},
        ).get("value")

    def title(self):
        return self.evaluate(
            "document.title"
        )

    def screenshot(self, path=None, format="png"):
        if format not in ("png", "jpeg", "webp"):
            raise ValueError(
                "format must be png, jpeg, or webp"
            )

        result = self.session.send(
            "Page.captureScreenshot",
            {
                "format": format,
            },
        )

        data = base64.b64decode(
            result["data"]
        )

        if path is not None:
            with open(path, "wb") as f:
                f.write(data)

        return data

    def wait_for_timeout(self, timeout):
        """
        Wait for a fixed amount of time.

        timeout is in milliseconds.
        """
        if timeout < 0:
            raise ValueError("timeout must be >= 0")

        time.sleep(timeout / 1000)

    def wait_for_selector(
        self,
        selector,
        timeout=5000,
        state="attached",
    ):
        """
        Wait until a selector reaches the requested state.

        state:
            attached
            visible
            hidden
            detached
        """
        if state not in (
            "attached",
            "visible",
            "hidden",
            "detached",
        ):
            raise ValueError(
                "state must be attached, visible, hidden, "
                "or detached"
            )

        deadline = time.monotonic() + (
            timeout / 1000
        )

        while True:
            try:
                exists = bool(
                    self.evaluate(
                        f"""(() => {{
                            const e =
                                document.querySelector(
                                    {json.dumps(selector)}
                                );

                            if (!e) return false;

                            if (
                                {json.dumps(state)}
                                === "attached"
                            ) {{
                                return true;
                            }}

                            const visible =
                                !!(
                                    e.offsetWidth ||
                                    e.offsetHeight ||
                                    e.getClientRects().length
                                );

                            if (
                                {json.dumps(state)}
                                === "visible"
                            ) {{
                                return visible;
                            }}

                            if (
                                {json.dumps(state)}
                                === "hidden"
                            ) {{
                                return !visible;
                            }}

                            return false;
                        }})()"""
                    )
                )

                if state == "detached":
                    if not exists:
                        return True

                elif exists:
                    return True

            except Exception:
                if state in ("hidden", "detached"):
                    return True

            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Timeout waiting for selector "
                    f"'{selector}' to be {state}"
                )

            time.sleep(0.05)

    def wait_for_function(
        self,
        expression,
        timeout=5000,
        polling=100,
    ):
        """
        Wait until a JavaScript expression returns a truthy value.

        expression:
            JavaScript expression or function call.

        polling:
            Polling interval in milliseconds.
        """
        if timeout < 0:
            raise ValueError("timeout must be >= 0")

        if polling <= 0:
            raise ValueError("polling must be > 0")

        deadline = time.monotonic() + (
            timeout / 1000
        )

        while True:
            result = self.evaluate(
                expression
            )

            if result:
                return result

            if time.monotonic() >= deadline:
                raise TimeoutError(
                    "Timeout waiting for function: "
                    f"{expression}"
                )

            time.sleep(polling / 1000)

    def wait_for_url(self, url, timeout=5000):
        """
        Wait until the current URL matches.

        Supports:
            exact URLs
            '*' wildcards
        """
        import fnmatch

        deadline = time.monotonic() + (
            timeout / 1000
        )

        while True:
            current = self.evaluate(
                "location.href"
            )

            if fnmatch.fnmatch(current, url):
                self._url = current
                return current

            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Timeout waiting for URL: {url}\n"
                    f"Current URL: {current}"
                )

            time.sleep(0.05)

    def close(self):
        self.session.send("Page.close")
