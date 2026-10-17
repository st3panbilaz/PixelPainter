"""Инструмент «Ластик» — рисует белым цветом."""

from PySide6.QtGui import QColor

from src.tools.base_tool import BaseTool


WHITE = QColor(255, 255, 255)


class EraserTool(BaseTool):
    name = "Ластик"
    tool_id = "eraser"

    def __init__(self):
        self._last = None

    def mouse_press(self, canvas, x, y, button):
        self._last = (x, y)
        canvas.set_pixel(x, y, WHITE)

    def mouse_move(self, canvas, x, y):
        if self._last is None:
            return
        if (x, y) != self._last:
            canvas.draw_line_pixels(self._last, (x, y), WHITE)
            self._last = (x, y)

    def mouse_release(self, canvas, x, y, button):
        self._last = None