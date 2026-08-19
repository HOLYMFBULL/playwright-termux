class BrowserContext:
    def __init__(self, browser, context_id):
        self.browser = browser
        self.context_id = context_id
        self._pages = []
        self._closed = False

    @property
    def is_closed(self):
        return self._closed

    def new_page(self):
        if self._closed:
            raise RuntimeError("BrowserContext is closed")

        result = self.browser.cdp.send(
            "Target.createTarget",
            {
                "url": "about:blank",
                "browserContextId": self.context_id,
            },
        )

        target_id = result["targetId"]

        session = self.browser.cdp.create_session(
            target_id
        )

        from .page import Page

        page = Page(
            self,
            session,
        )

        self._pages.append(page)

        return page

    def cookies(self, urls=None):
        """
        Return cookies belonging to this browser context.
        """
        if self._closed:
            raise RuntimeError("BrowserContext is closed")

        result = self.browser.cdp.send(
            "Storage.getCookies",
            {
                "browserContextId": self.context_id,
            },
        )

        cookies = result.get("cookies", [])

        if urls is None:
            return cookies

        if isinstance(urls, str):
            urls = [urls]

        return [
            cookie
            for cookie in cookies
            if any(
                url.startswith(
                    cookie.get("domain", "")
                )
                for url in urls
            )
        ]

    def add_cookies(self, cookies):
        """
        Add cookies to this browser context.
        """
        if self._closed:
            raise RuntimeError("BrowserContext is closed")

        if not isinstance(cookies, list):
            raise TypeError(
                "cookies must be a list"
            )

        self.browser.cdp.send(
            "Storage.setCookies",
            {
                "cookies": cookies,
                "browserContextId": self.context_id,
            },
        )

    def clear_cookies(self):
        """
        Clear cookies belonging to this browser context.
        """
        if self._closed:
            return

        self.browser.cdp.send(
            "Storage.clearCookies",
            {
                "browserContextId": self.context_id,
            },
        )

    def close(self):
        if self._closed:
            return

        self._closed = True

        # Close pages belonging to this context.
        for page in list(self._pages):
            try:
                page.close()
            except Exception:
                pass

        self._pages.clear()

        try:
            self.browser.cdp.send(
                "Target.disposeBrowserContext",
                {
                    "browserContextId": self.context_id,
                },
            )
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
