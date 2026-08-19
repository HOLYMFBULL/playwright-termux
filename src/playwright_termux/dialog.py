
import threading


class Dialog:
    """Represents a JavaScript alert/confirm/prompt dialog."""

    def __init__(
        self,
        page,
        type_,
        message="",
        default_value="",
    ):
        self.page = page
        self.type = type_
        self.message = message
        self.default_value = default_value
        self._handled = False

    def accept(self, prompt_text=None):
        if self._handled:
            return

        params = {
            "accept": True,
        }

        if prompt_text is not None:
            params["promptText"] = str(prompt_text)

        self.page.session.send(
            "Page.handleJavaScriptDialog",
            params,
        )

        self._handled = True

    def dismiss(self):
        if self._handled:
            return

        self.page.session.send(
            "Page.handleJavaScriptDialog",
            {"accept": False},
        )

        self._handled = True

    def __repr__(self):
        return (
            f"<Dialog type={self.type!r} "
            f"message={self.message!r}>"
        )
