from pathlib import Path

path = Path("src/playwright_termux/page.py")
text = path.read_text()

marker = '    def locator(self, selector):\n'

methods = '''    def go_back(self, timeout=30):
        """Navigate to the previous entry in browser history."""
        history = self.session.send("Page.getNavigationHistory")
        entries = history.get("entries", [])
        current_index = history.get("currentIndex", -1)

        if current_index <= 0:
            return None

        entry_id = entries[current_index - 1]["id"]

        self.session.send(
            "Page.navigateToHistoryEntry",
            {"entryId": entry_id},
        )

        self._wait_for_navigation(timeout)
        self._url = self.evaluate("location.href")
        return self

    def go_forward(self, timeout=30):
        """Navigate to the next entry in browser history."""
        history = self.session.send("Page.getNavigationHistory")
        entries = history.get("entries", [])
        current_index = history.get("currentIndex", -1)

        if current_index < 0 or current_index >= len(entries) - 1:
            return None

        entry_id = entries[current_index + 1]["id"]

        self.session.send(
            "Page.navigateToHistoryEntry",
            {"entryId": entry_id},
        )

        self._wait_for_navigation(timeout)
        self._url = self.evaluate("location.href")
        return self

'''

if 'def go_back(self, timeout=30):' in text:
    print("History methods already exist.")
else:
    text = text.replace(marker, methods + marker)
    path.write_text(text)
    print("History methods added.")
