"""Инструмент «Карандаш»."""

from PySide6.QtCore import Qt

from src.tools.base_tool import BaseTool


class PencilTool(BaseTool):
    name = "Карандаш"
    tool_id = "pencil"

    def __init__(self):
        self._last = None
        self._color = None

    def _color_for(self, canvas, button):
        if button == Qt.MouseButton.RightButton:
            return canvas.secondary_color()
        return canvas.primary_color()

    def mouse_press(self, canvas, x, y, button):
        self._color = self._color_for(canvas, button)
        self._last = (x, y)
        canvas.set_pixel(x, y, self._color)

    def mouse_move(self, canvas, x, y):
        if self._last is None:
            return
        if (x, y) != self._last:
            canvas.draw_line_pixels(self._last, (x, y), self._color)
            self._last = (x, y)

    def mouse_release(self, canvas, x, y, button):
        self._last = None
        self._color = None