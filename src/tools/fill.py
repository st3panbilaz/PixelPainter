"""Инструмент «Заливка» (flood fill)."""

from PySide6.QtCore import Qt

from src.tools.base_tool import BaseTool


class FillTool(BaseTool):
    name = "Заливка"
    tool_id = "fill"

    def mouse_press(self, canvas, x, y, button):
        if button == Qt.MouseButton.RightButton:
            color = canvas.secondary_color()
        else:
            color = canvas.primary_color()
        canvas.flood_fill(x, y, color)

    def mouse_move(self, canvas, x, y):
        pass

    def mouse_release(self, canvas, x, y, button):
        pass