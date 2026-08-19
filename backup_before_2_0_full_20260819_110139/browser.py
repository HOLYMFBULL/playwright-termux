import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request

from .cdp import CDPConnection
from .page import Page


CHROMIUM_PATH = "/data/data/com.termux/files/usr/bin/chromium-browser"


class Chromium:
    def __init__(
        self,
        executable=CHROMIUM_PATH,
        port=9222,
        headless=False,
    ):
        self.executable = executable
        self.port = port
        self.headless = headless
        self.process = None
        self.cdp = None
        self.user_data_dir = None

    def launch(self):
        if not self.headless and not os.environ.get("DISPLAY"):
            raise RuntimeError(
                "Headed Chromium requires an X11 display. "
                "Start Termux:X11 and set DISPLAY, for example: DISPLAY=:0"
            )

        self.user_data_dir = tempfile.mkdtemp(
            prefix="playwright-termux-"
        )

        args = [
            self.executable,
            f"--remote-debugging-port={self.port}",
            "--remote-debugging-address=127.0.0.1",
            "--remote-allow-origins=http://127.0.0.1:9222",
            f"--user-data-dir={self.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
        ]

        if self.headless:
            args.append("--headless=new")

        print("[playwright-termux] Starting Chromium...")

        self.process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        endpoint = f"http://127.0.0.1:{self.port}/json/version"

        last_error = None

        for _ in range(100):
            if self.process.poll() is not None:
                output = self.process.stdout.read()
                raise RuntimeError(
                    "Chromium exited before CDP became available.\n"
                    f"Chromium output:\n{output}"
                )

            try:
                with urllib.request.urlopen(
                    endpoint,
                    timeout=1,
                ) as response:
                    info = json.load(response)

                ws_url = info.get("webSocketDebuggerUrl")

                if not ws_url:
                    raise RuntimeError(
                        "Chromium did not provide a "
                        "webSocketDebuggerUrl"
                    )

                self.cdp = CDPConnection(ws_url).connect()

                print("[playwright-termux] CDP connected.")

                return self

            except Exception as exc:
                last_error = exc
                time.sleep(0.1)

        self.close()

        raise RuntimeError(
            "Could not connect to Chromium CDP.\n"
            f"Last error: {last_error}"
        )

    def new_context(self):
        """
        Create an isolated Chromium browser context.
        """
        if not self.cdp:
            raise RuntimeError(
                "Chromium is not connected"
            )

        result = self.cdp.send(
            "Target.createBrowserContext",
            {},
        )

        context_id = result.get(
            "browserContextId"
        )

        if not context_id:
            raise RuntimeError(
                "Chromium did not return "
                "a browserContextId"
            )

        from .context import BrowserContext

        return BrowserContext(
            self,
            context_id,
        )

    def new_page(self):
        result = self.cdp.send(
            "Target.createTarget",
            {
                "url": "about:blank",
            },
        )

        target_id = result["targetId"]
        session = self.cdp.create_session(target_id)

        return Page(self, session)

    def close(self):
        if self.cdp:
            self.cdp.close()
            self.cdp = None

        if self.process:
            self.process.terminate()

            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()

            self.process = None

        if self.user_data_dir:
            shutil.rmtree(
                self.user_data_dir,
                ignore_errors=True,
            )

            self.user_data_dir = None

    def __enter__(self):
        return self.launch()

    def __exit__(self, exc_type, exc, tb):
        self.close()
