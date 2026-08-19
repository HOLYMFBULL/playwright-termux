class Mouse:
    def __init__(self, page):
        self.page = page
        self.session = page.session
        self._x = 0.0
        self._y = 0.0

    def move(self, x, y):
        self._x = float(x)
        self._y = float(y)

        self.session.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseMoved",
                "x": self._x,
                "y": self._y,
            },
        )

    def down(self, button="left", click_count=1):
        self.session.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mousePressed",
                "x": self._x,
                "y": self._y,
                "button": button,
                "clickCount": click_count,
            },
        )

    def up(self, button="left", click_count=1):
        self.session.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseReleased",
                "x": self._x,
                "y": self._y,
                "button": button,
                "clickCount": click_count,
            },
        )

    def click(self, x, y, button="left", click_count=1):
        self.move(x, y)

        self.session.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mousePressed",
                "x": float(x),
                "y": float(y),
                "button": button,
                "clickCount": click_count,
            },
        )

        self.session.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseReleased",
                "x": float(x),
                "y": float(y),
                "button": button,
                "clickCount": click_count,
            },
        )

    def wheel(self, delta_x=0, delta_y=0):
        self.session.send(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseWheel",
                "x": self._x,
                "y": self._y,
                "deltaX": float(delta_x),
                "deltaY": float(delta_y),
            },
        )
