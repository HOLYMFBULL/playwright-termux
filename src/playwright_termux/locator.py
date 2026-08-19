import json
import time


class Locator:
    def __init__(self, page, selector):
        self.page = page
        self.selector = selector

    def _selector(self):
        return json.dumps(self.selector)

    def _resolve_node(self, timeout=5000, state="attached"):
        """
        Resolve the first matching DOM node.

        state:
            attached - element exists
            visible  - element exists and is visible
        """

        deadline = time.monotonic() + (timeout / 1000)

        while True:
            document = self.page.session.send(
                "DOM.getDocument",
                {"depth": -1},
            )

            result = self.page.session.send(
                "DOM.querySelector",
                {
                    "nodeId": document["root"]["nodeId"],
                    "selector": self.selector,
                },
            )

            node_id = result.get("nodeId", 0)

            if node_id:
                if state == "attached":
                    return node_id

                if state == "visible":
                    visible = self.page.evaluate(
                        f"""(() => {{
                            const e =
                                document.querySelector(
                                    {self._selector()}
                                );

                            if (!e) return false;

                            const r = e.getBoundingClientRect();
                            const s = getComputedStyle(e);

                            return (
                                r.width > 0 &&
                                r.height > 0 &&
                                s.display !== "none" &&
                                s.visibility !== "hidden"
                            );
                        }})()"""
                    )

                    if visible:
                        return node_id

            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Timeout {timeout}ms exceeded "
                    f"while waiting for "
                    f"{self.selector!r}"
                )

            time.sleep(0.05)

    def is_visible(self, timeout=0):
        try:
            self._resolve_node(
                timeout,
                state="visible",
            )
            return True
        except TimeoutError:
            return False

    def is_enabled(self, timeout=0):
        try:
            self._resolve_node(timeout)

            return bool(
                self.page.evaluate(
                    f"""(() => {{
                        const element =
                            document.querySelector(
                                {self._selector()}
                            );

                        if (!element) return false;

                        return !element.disabled;
                    }})()"""
                )
            )

        except TimeoutError:
            return False

    def is_checked(self, timeout=5000):
        self._resolve_node(timeout)

        return bool(
            self.page.evaluate(
                f"""(() => {{
                    const e =
                        document.querySelector(
                            {self._selector()}
                        );

                    return !!e && !!e.checked;
                }})()"""
            )
        )

    def check(self, timeout=5000):
        self._resolve_node(
            timeout,
            state="visible",
        )

        return self.page.evaluate(
            f"""(() => {{
                const e =
                    document.querySelector(
                        {self._selector()}
                    );

                if (!e) {{
                    throw new Error(
                        "Element disappeared: "
                        + {self._selector()}
                    );
                }}

                if (
                    e.type !== "checkbox" &&
                    e.type !== "radio"
                ) {{
                    throw new Error(
                        "check() requires a checkbox or radio"
                    );
                }}

                if (!e.checked) {{
                    e.click();
                }}

                return e.checked;
            }})()"""
        )

    def uncheck(self, timeout=5000):
        self._resolve_node(
            timeout,
            state="visible",
        )

        return self.page.evaluate(
            f"""(() => {{
                const e =
                    document.querySelector(
                        {self._selector()}
                    );

                if (!e) {{
                    throw new Error(
                        "Element disappeared: "
                        + {self._selector()}
                    );
                }}

                if (e.type !== "checkbox") {{
                    throw new Error(
                        "uncheck() requires a checkbox"
                    );
                }}

                if (e.checked) {{
                    e.click();
                }}

                return !e.checked;
            }})()"""
        )

    def input_value(self, timeout=5000):
        self._resolve_node(timeout)

        return self.page.evaluate(
            f"""(() => {{
                const e = document.querySelector(
                    {self._selector()}
                );

                if (!e) {{
                    throw new Error("Element not found");
                }}

                return e.value;
            }})()"""
        )

    def set_input_files(self, files, timeout=5000):
        """
        Set files on an <input type="file"> element.

        Examples:
            locator.set_input_files("photo.png")
            locator.set_input_files(["one.png", "two.png"])
        """
        from pathlib import Path

        self._resolve_node(
            timeout,
            state="visible",
        )

        if isinstance(files, (str, Path)):
            files = [files]
        elif isinstance(files, (list, tuple)):
            files = list(files)
        else:
            raise TypeError(
                "files must be a path or a list of paths"
            )

        paths = []

        for file in files:
            path = Path(file).expanduser().resolve()

            if not path.is_file():
                raise FileNotFoundError(
                    f"File does not exist: {path}"
                )

            paths.append(str(path))

        # Resolve the DOM node again so we get its current nodeId.
        document = self.page.session.send(
            "DOM.getDocument",
            {"depth": -1},
        )

        result = self.page.session.send(
            "DOM.querySelector",
            {
                "nodeId": document["root"]["nodeId"],
                "selector": self.selector,
            },
        )

        node_id = result.get("nodeId", 0)

        if not node_id:
            raise RuntimeError(
                f"Element not found: {self.selector}"
            )

        # Verify that the target is actually a file input.
        tag_result = self.page.evaluate(
            f"""(() => {{
                const e = document.querySelector(
                    {self._selector()}
                );

                if (!e) return null;

                return {{
                    tag: e.tagName,
                    type: e.type
                }};
            }})()"""
        )

        if not tag_result:
            raise RuntimeError(
                f"Element not found: {self.selector}"
            )

        if (
            tag_result["tag"] != "INPUT"
            or tag_result["type"] != "file"
        ):
            raise TypeError(
                "set_input_files() requires "
                '<input type="file">'
            )

        self.page.session.send(
            "DOM.setFileInputFiles",
            {
                "nodeId": node_id,
                "files": paths,
            },
        )

        return paths

    def select_option(
        self,
        value=None,
        *,
        label=None,
        index=None,
        timeout=5000,
    ):
        self._resolve_node(
            timeout,
            state="visible",
        )

        if sum(
            x is not None
            for x in (value, label, index)
        ) != 1:
            raise ValueError(
                "select_option() requires exactly "
                "one of value, label, or index"
            )

        # Convert Python values into safe JSON literals.
        import json

        value_js = (
            json.dumps(value)
            if value is not None
            else "null"
        )

        label_js = (
            json.dumps(label)
            if label is not None
            else "null"
        )

        index_js = (
            str(index)
            if index is not None
            else "null"
        )

        return self.page.evaluate(
            f"""(() => {{
                const e = document.querySelector(
                    {self._selector()}
                );

                if (!e) {{
                    throw new Error("Element not found");
                }}

                if (e.tagName !== "SELECT") {{
                    throw new Error(
                        "select_option() requires a <select>"
                    );
                }}

                let selected = null;

                if ({value_js} !== null) {{
                    const option = Array.from(e.options)
                        .find(o => o.value === {value_js});

                    if (!option) {{
                        throw new Error(
                            "Option value not found: "
                            + {value_js}
                        );
                    }}

                    e.value = option.value;
                    selected = option.value;

                }} else if ({label_js} !== null) {{
                    const option = Array.from(e.options)
                        .find(o => o.textContent.trim() === {label_js});

                    if (!option) {{
                        throw new Error(
                            "Option label not found: "
                            + {label_js}
                        );
                    }}

                    e.value = option.value;
                    selected = option.value;

                }} else {{
                    const i = {index_js};

                    if (
                        i < 0 ||
                        i >= e.options.length
                    ) {{
                        throw new Error(
                            "Option index out of range: " + i
                        );
                    }}

                    e.selectedIndex = i;
                    selected = e.options[i].value;
                }}

                e.dispatchEvent(
                    new Event("input", {{
                        bubbles: true
                    }})
                );

                e.dispatchEvent(
                    new Event("change", {{
                        bubbles: true
                    }})
                );

                return selected;
            }})()"""
        )

    def wait_for(
        self,
        timeout=5000,
        state="attached",
    ):
        """
        Wait for this locator to reach a state.
        """
        self.page.wait_for_selector(
            self.selector,
            timeout=timeout,
            state=state,
        )

        return self

    def count(self):
        return self.page.evaluate(
            f"document.querySelectorAll({self._selector()}).length"
        )

    def text_content(self, timeout=5000):
        self._resolve_node(timeout)

        return self.page.evaluate(
            f"""(() => {{
                const element =
                    document.querySelector({self._selector()});
                return element ? element.textContent : null;
            }})()"""
        )

    def get_attribute(self, name, timeout=5000):
        self._resolve_node(timeout)

        return self.page.evaluate(
            f"""(() => {{
                const element =
                    document.querySelector({self._selector()});

                return element
                    ? element.getAttribute(
                        {json.dumps(name)}
                    )
                    : null;
            }})()"""
        )

    def fill(self, value, timeout=5000):
        self._resolve_node(
            timeout,
            state="visible",
        )

        value_json = json.dumps(str(value))

        expression = f"""(() => {{
            const element =
                document.querySelector(
                    {self._selector()}
                );

            if (!element) {{
                throw new Error(
                    "Element disappeared: "
                    + {self._selector()}
                );
            }}

            element.focus();
            element.value = {value_json};

            element.dispatchEvent(
                new Event(
                    "input",
                    {{ bubbles: true }}
                )
            );

            element.dispatchEvent(
                new Event(
                    "change",
                    {{ bubbles: true }}
                )
            );

            return true;
        }})()"""

        return self.page.evaluate(expression)

    def _get_center(self, node_id):
        box = self.page.session.send(
            "DOM.getBoxModel",
            {"nodeId": node_id},
        )

        model = box["model"]
        quad = model["content"]

        x = (
            quad[0]
            + quad[2]
            + quad[4]
            + quad[6]
        ) / 4

        y = (
            quad[1]
            + quad[3]
            + quad[5]
            + quad[7]
        ) / 4

        return x, y

    def scroll_into_view_if_needed(self, timeout=5000):
        self._resolve_node(
            timeout,
            state="visible",
        )

        return self.page.evaluate(
            f"""(() => {{
                const element =
                    document.querySelector(
                        {self._selector()}
                    );

                if (!element) return false;

                element.scrollIntoView({{
                    behavior: "instant",
                    block: "center",
                    inline: "center"
                }});

                return true;
            }})()"""
        )

    def click(self, timeout=5000):
        self.scroll_into_view_if_needed(timeout)

        node_id = self._resolve_node(
            timeout,
            state="visible",
        )

        x, y = self._get_center(node_id)

        session = self.page.session

        session.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseMoved",
                "x": x,
                "y": y,
            },
        )

        session.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mousePressed",
                "x": x,
                "y": y,
                "button": "left",
                "clickCount": 1,
            },
        )

        session.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseReleased",
                "x": x,
                "y": y,
                "button": "left",
                "clickCount": 1,
            },
        )

        return True

    def press(self, key, timeout=5000):
        node_id = self._resolve_node(
            timeout,
            state="visible",
        )

        self.page.session.send(
            "DOM.focus",
            {"nodeId": node_id},
        )

        key_info = {
            "Enter": {
                "key": "Enter",
                "code": "Enter",
                "windowsVirtualKeyCode": 13,
                "nativeVirtualKeyCode": 13,
            },
            "Tab": {
                "key": "Tab",
                "code": "Tab",
                "windowsVirtualKeyCode": 9,
                "nativeVirtualKeyCode": 9,
            },
            "Escape": {
                "key": "Escape",
                "code": "Escape",
                "windowsVirtualKeyCode": 27,
                "nativeVirtualKeyCode": 27,
            },
            "Backspace": {
                "key": "Backspace",
                "code": "Backspace",
                "windowsVirtualKeyCode": 8,
                "nativeVirtualKeyCode": 8,
            },
            "ArrowUp": {
                "key": "ArrowUp",
                "code": "ArrowUp",
                "windowsVirtualKeyCode": 38,
                "nativeVirtualKeyCode": 38,
            },
            "ArrowDown": {
                "key": "ArrowDown",
                "code": "ArrowDown",
                "windowsVirtualKeyCode": 40,
                "nativeVirtualKeyCode": 40,
            },
            "ArrowLeft": {
                "key": "ArrowLeft",
                "code": "ArrowLeft",
                "windowsVirtualKeyCode": 37,
                "nativeVirtualKeyCode": 37,
            },
            "ArrowRight": {
                "key": "ArrowRight",
                "code": "ArrowRight",
                "windowsVirtualKeyCode": 39,
                "nativeVirtualKeyCode": 39,
            },
            "Space": {
                "key": " ",
                "code": "Space",
                "windowsVirtualKeyCode": 32,
                "nativeVirtualKeyCode": 32,
            },
        }

        info = key_info.get(
            key,
            {
                "key": key,
                "code": (
                    f"Key{key.upper()}"
                    if len(key) == 1 and key.isalpha()
                    else key
                ),
                "windowsVirtualKeyCode": (
                    ord(key.upper())
                    if len(key) == 1
                    else 0
                ),
                "nativeVirtualKeyCode": (
                    ord(key.upper())
                    if len(key) == 1
                    else 0
                ),
            },
        )

        down = {
            "type": "keyDown",
            **info,
        }

        if len(key) == 1:
            down["text"] = key

        self.page.session.send(
            "Input.dispatchKeyEvent",
            down,
        )

        self.page.session.send(
            "Input.dispatchKeyEvent",
            {
                "type": "keyUp",
                **info,
            },
        )

        return True
