import time


class Keyboard:
    MODIFIERS = {
        "Alt": {
            "key": "Alt",
            "code": "AltLeft",
            "windowsVirtualKeyCode": 18,
        },
        "Control": {
            "key": "Control",
            "code": "ControlLeft",
            "windowsVirtualKeyCode": 17,
        },
        "Ctrl": {
            "key": "Control",
            "code": "ControlLeft",
            "windowsVirtualKeyCode": 17,
        },
        "Shift": {
            "key": "Shift",
            "code": "ShiftLeft",
            "windowsVirtualKeyCode": 16,
        },
        "Meta": {
            "key": "Meta",
            "code": "MetaLeft",
            "windowsVirtualKeyCode": 91,
        },
    }

    SPECIAL_KEYS = {
        "Enter": ("Enter", "Enter", 13),
        "Tab": ("Tab", "Tab", 9),
        "Escape": ("Escape", "Escape", 27),
        "Backspace": ("Backspace", "Backspace", 8),
        "Delete": ("Delete", "Delete", 46),
        "ArrowUp": ("ArrowUp", "ArrowUp", 38),
        "ArrowDown": ("ArrowDown", "ArrowDown", 40),
        "ArrowLeft": ("ArrowLeft", "ArrowLeft", 37),
        "ArrowRight": ("ArrowRight", "ArrowRight", 39),
        "Home": ("Home", "Home", 36),
        "End": ("End", "End", 35),
        "PageUp": ("PageUp", "PageUp", 33),
        "PageDown": ("PageDown", "PageDown", 34),
        "Space": (" ", "Space", 32),
    }

    def __init__(self, page):
        self.page = page
        self.session = page.session
        self._modifiers = set()

    def _key_info(self, key):
        if key in self.MODIFIERS:
            info = self.MODIFIERS[key].copy()
            info["type_key"] = key
            return info

        if key in self.SPECIAL_KEYS:
            value = self.SPECIAL_KEYS[key]

            return {
                "key": value[0],
                "code": value[1],
                "windowsVirtualKeyCode": value[2],
            }

        if len(key) == 1:
            upper = key.upper()

            return {
                "key": key,
                "code": (
                    f"Key{upper}"
                    if key.isalpha()
                    else key
                ),
                "windowsVirtualKeyCode": ord(upper),
            }

        # Function keys
        if key.startswith("F") and key[1:].isdigit():
            number = int(key[1:])

            if 1 <= number <= 12:
                return {
                    "key": key,
                    "code": key,
                    "windowsVirtualKeyCode": 111 + number,
                }

        raise ValueError(
            f"Unsupported key: {key}"
        )

    def down(self, key):
        info = self._key_info(key)

        if key in self.MODIFIERS:
            self._modifiers.add(key)

        modifiers = self._modifier_mask()

        params = {
            "type": "keyDown",
            "key": info["key"],
            "code": info["code"],
            "modifiers": modifiers,
        }

        if "windowsVirtualKeyCode" in info:
            params["windowsVirtualKeyCode"] = (
                info["windowsVirtualKeyCode"]
            )

        if len(key) == 1 and not self._modifiers:
            params["text"] = key

        self.session.send(
            "Input.dispatchKeyEvent",
            params,
        )

    def up(self, key):
        info = self._key_info(key)

        modifiers = self._modifier_mask()

        params = {
            "type": "keyUp",
            "key": info["key"],
            "code": info["code"],
            "modifiers": modifiers,
        }

        if "windowsVirtualKeyCode" in info:
            params["windowsVirtualKeyCode"] = (
                info["windowsVirtualKeyCode"]
            )

        self.session.send(
            "Input.dispatchKeyEvent",
            params,
        )

        if key in self.MODIFIERS:
            self._modifiers.discard(key)

    def press(self, key):
        """
        Supports:
            Enter
            Tab
            ArrowDown
            a
            Control+A
            Shift+Tab
        """

        parts = key.split("+")

        modifiers = parts[:-1]
        main_key = parts[-1]

        for modifier in modifiers:
            self.down(modifier)

        self.down(main_key)
        self.up(main_key)

        for modifier in reversed(modifiers):
            self.up(modifier)

    def insert_text(self, text):
        self.session.send(
            "Input.insertText",
            {
                "text": str(text),
            },
        )

    def type(self, text, delay=0):
        """
        Types text character-by-character.
        """

        for char in str(text):
            self.insert_text(char)

            if delay:
                time.sleep(delay / 1000)

    def _modifier_mask(self):
        mask = 0

        if self._has_modifier("Alt"):
            mask |= 1

        if self._has_modifier("Control"):
            mask |= 2

        if self._has_modifier("Meta"):
            mask |= 4

        if self._has_modifier("Shift"):
            mask |= 8

        return mask

    def _has_modifier(self, name):
        return (
            name in self._modifiers
            or (
                name == "Control"
                and "Ctrl" in self._modifiers
            )
        )
