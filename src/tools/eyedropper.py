"""Инструмент «Пипетка» — берёт цвет пикселя с холста."""

from PySide6.QtCore import Qt

from src.tools.base_tool import BaseTool


class EyedropperTool(BaseTool):
    name = "Пипетка"
    tool_id = "eyedropper"

    def mouse_press(self, canvas, x, y, button):
        color = canvas.get_pixel(x, y)
        target = "secondary" if button == Qt.MouseButton.RightButton else "primary"
        canvas.color_picked.emit(color, target)

    def mouse_move(self, canvas, x, y):
        pass

    def mouse_release(self, canvas, x, y, button):
        pass