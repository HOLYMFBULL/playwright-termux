
class Frame:
    """A lightweight CDP-backed iframe wrapper."""

    def __init__(self, page, frame_id=None, name=None, url=None):
        self.page = page
        self.frame_id = frame_id
        self.name = name
        self.url = url

    def evaluate(self, expression):
        if not self.frame_id:
            return self.page.evaluate(expression)

        result = self.page.session.send(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True,
            },
        )

        if "exceptionDetails" in result:
            raise RuntimeError(
                result["exceptionDetails"].get(
                    "text",
                    "Frame evaluation failed",
                )
            )

        return result.get("result", {}).get("value")

    def locator(self, selector):
        from .locator import Locator
        return Locator(self.page, selector, frame=self)

    def title(self):
        return self.evaluate("document.title")

    def content(self):
        return self.evaluate("document.documentElement.outerHTML")

    def __repr__(self):
        return (
            f"<Frame name={self.name!r} "
            f"url={self.url!r}>"
        )
