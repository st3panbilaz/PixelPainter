"""Базовый класс инструмента."""


class BaseTool:
    """Абстрактный инструмент. Все инструменты наследуются от него."""

    name = "Инструмент"
    tool_id = "base"

    def mouse_press(self, canvas, x: int, y: int, button):
        """Нажатие кнопки мыши внутри холста. x, y — координаты пикселя."""
        pass

    def mouse_move(self, canvas, x: int, y: int):
        """Движение мыши с зажатой кнопкой."""
        pass

    def mouse_release(self, canvas, x: int, y: int, button):
        """Отпускание кнопки мыши."""
        pass