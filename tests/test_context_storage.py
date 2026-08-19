from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from playwright_termux.browser import Chromium


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"""
        <!doctype html>
        <html>
        <body>
        Context storage test
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def test_context_storage():
    server = HTTPServer(("127.0.0.1", 0), Handler)

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    url = f"http://127.0.0.1:{server.server_port}/"

    try:
        with Chromium(headless=True) as browser:
            context1 = browser.new_context()
            context2 = browser.new_context()

            page1 = context1.new_page()
            page2 = context2.new_page()

            page1.goto(url)
            page2.goto(url)

            page1.evaluate("""
                () => {
                    localStorage.setItem("user", "context-one");
                    sessionStorage.setItem("session", "context-one");
                }
            """)

            # Context 1 has its own localStorage.
            assert page1.evaluate(
                "localStorage.getItem('user')"
            ) == "context-one"

            # Context 2 must not see Context 1's localStorage.
            assert page2.evaluate(
                "localStorage.getItem('user')"
            ) is None

            # Context 1 has its own sessionStorage.
            assert page1.evaluate(
                "sessionStorage.getItem('session')"
            ) == "context-one"

            # Context 2 must not see Context 1's sessionStorage.
            assert page2.evaluate(
                "sessionStorage.getItem('session')"
            ) is None

            context1.close()
            context2.close()

    finally:
        server.shutdown()
        server.server_close()
