import json
import threading
import time

import websocket


class CDPError(Exception):
    """Raised when a CDP command fails."""


class CDPSession:
    def __init__(self, connection, session_id):
        self.connection = connection
        self.session_id = session_id

    def off(self, event_name, callback):
        self.connection.off(
            event_name,
            callback,
            session_id=self.session_id,
        )

    def send(self, method, params=None, timeout=None):
        return self.connection.send(
            method,
            params=params,
            session_id=self.session_id,
            timeout=timeout,
        )

    def on(self, event_name, callback):
        self.connection.on(
            event_name,
            callback,
            session_id=self.session_id,
        )


class CDPConnection:
    def __init__(self, ws_url, timeout=10):
        self.ws_url = ws_url
        self.timeout = timeout

        self._ws = None
        self._connected = False

        self._next_id = 0
        self._id_lock = threading.Lock()

        self._pending = {}
        self._pending_lock = threading.Lock()

        self._events = {}
        self._events_lock = threading.Lock()

        self._receiver = None

    def connect(self):
        if self._connected:
            return self

        self._ws = websocket.create_connection(
            self.ws_url,
            timeout=self.timeout,
        )

        self._connected = True

        self._receiver = threading.Thread(
            target=self._receive_loop,
            name="playwright-termux-cdp",
            daemon=True,
        )

        self._receiver.start()

        return self

    def close(self):
        if not self._connected:
            return

        self._connected = False

        if self._ws is not None:
            try:
                self._ws.close()
            except Exception:
                pass

        self._ws = None

        with self._pending_lock:
            pending = list(self._pending.values())
            self._pending.clear()

        for item in pending:
            item["error"] = CDPError("CDP connection closed")
            item["event"].set()

    def _receive_loop(self):
        while self._connected and self._ws is not None:
            try:
                raw = self._ws.recv()

                if not raw:
                    break

                message = json.loads(raw)

                # Command response.
                if "id" in message:
                    command_id = message["id"]

                    with self._pending_lock:
                        pending = self._pending.get(command_id)

                    if pending is not None:
                        pending["response"] = message
                        pending["event"].set()

                    continue

                # CDP event.
                method = message.get("method")

                if method:
                    self._emit(
                        method,
                        message.get("params", {}),
                        message.get("sessionId"),
                    )

            except Exception as exc:
                if self._connected:
                    with self._pending_lock:
                        pending = list(self._pending.values())

                    for item in pending:
                        item["error"] = exc
                        item["event"].set()

                break

        self._connected = False

    def off(self, event_name, callback, session_id=None):
        key = (session_id, event_name)

        with self._events_lock:
            callbacks = self._events.get(key)

            if not callbacks:
                return

            try:
                callbacks.remove(callback)
            except ValueError:
                pass

            if not callbacks:
                self._events.pop(key, None)

    def _emit(self, event_name, params, session_id):
        with self._events_lock:
            callbacks = list(
                self._events.get(
                    (session_id, event_name),
                    [],
                )
            )

            callbacks += self._events.get(
                (None, event_name),
                [],
            )

        for callback in callbacks:
            try:
                callback(params)
            except Exception:
                pass

    def on(self, event_name, callback, session_id=None):
        key = (session_id, event_name)

        with self._events_lock:
            self._events.setdefault(key, []).append(callback)

    def _next_command_id(self):
        with self._id_lock:
            self._next_id += 1
            return self._next_id

    def send(
        self,
        method,
        params=None,
        session_id=None,
        timeout=None,
    ):
        if not self._connected or self._ws is None:
            raise CDPError("CDP connection is not open")

        command_id = self._next_command_id()

        message = {
            "id": command_id,
            "method": method,
        }

        if params is not None:
            message["params"] = params

        if session_id is not None:
            message["sessionId"] = session_id

        waiter = {
            "event": threading.Event(),
            "response": None,
            "error": None,
        }

        with self._pending_lock:
            self._pending[command_id] = waiter

        try:
            self._ws.send(json.dumps(message))

            wait_timeout = (
                self.timeout
                if timeout is None
                else timeout
            )

            if not waiter["event"].wait(wait_timeout):
                raise CDPError(
                    f"Timeout waiting for CDP command: {method}"
                )

            if waiter["error"] is not None:
                raise CDPError(str(waiter["error"]))

            response = waiter["response"]

            if response is None:
                raise CDPError(
                    f"No response received for: {method}"
                )

            if "error" in response:
                raise CDPError(response["error"])

            return response.get("result", {})

        finally:
            with self._pending_lock:
                self._pending.pop(command_id, None)

    def create_session(self, target_id):
        result = self.send(
            "Target.attachToTarget",
            {
                "targetId": target_id,
                "flatten": True,
            },
        )

        return CDPSession(
            self,
            result["sessionId"],
        )

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc, tb):
        self.close()
