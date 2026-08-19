
class Request:
    def __init__(self, params):
        self.params = params
        self.url = params.get("request", {}).get("url")
        self.method = params.get("request", {}).get("method")
        self.headers = params.get("request", {}).get("headers", {})
        self.post_data = params.get("request", {}).get("postData")


class Response:
    def __init__(self, params):
        self.params = params
        self.url = params.get("response", {}).get("url")
        self.status = params.get("response", {}).get("status")
        self.status_text = params.get("response", {}).get("statusText")
        self.headers = params.get("response", {}).get("headers", {})


class Network:
    """Network event monitoring for a Page."""

    def __init__(self, page):
        self.page = page
        self._request_callbacks = []
        self._response_callbacks = []
        self._enabled = False

    def enable(self):
        if self._enabled:
            return

        self.page.session.send("Network.enable")

        self.page.session.on(
            "Network.requestWillBeSent",
            self._request_event,
        )

        self.page.session.on(
            "Network.responseReceived",
            self._response_event,
        )

        self._enabled = True

    def _request_event(self, params):
        request = Request(params)

        for callback in list(self._request_callbacks):
            try:
                callback(request)
            except Exception:
                pass

    def _response_event(self, params):
        response = Response(params)

        for callback in list(self._response_callbacks):
            try:
                callback(response)
            except Exception:
                pass

    def on_request(self, callback):
        self.enable()
        self._request_callbacks.append(callback)
        return callback

    def on_response(self, callback):
        self.enable()
        self._response_callbacks.append(callback)
        return callback

    def off_request(self, callback):
        try:
            self._request_callbacks.remove(callback)
        except ValueError:
            pass

    def off_response(self, callback):
        try:
            self._response_callbacks.remove(callback)
        except ValueError:
            pass

    def disable(self):
        if not self._enabled:
            return

        self.page.session.off(
            "Network.requestWillBeSent",
            self._request_event,
        )

        self.page.session.off(
            "Network.responseReceived",
            self._response_event,
        )

        try:
            self.page.session.send("Network.disable")
        except Exception:
            pass

        self._enabled = False
