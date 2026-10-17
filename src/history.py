"""История изменений холста (Undo/Redo)."""

from PySide6.QtGui import QImage


class History:
    """Хранит снимки QImage. Стек ограничен по глубине."""

    def __init__(self, limit: int = 50):
        self._undo_stack: list[QImage] = []
        self._redo_stack: list[QImage] = []
        self._limit = limit

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()

    def push(self, image: QImage):
        """Сохранить снимок перед изменением."""
        self._undo_stack.append(image.copy())
        if len(self._undo_stack) > self._limit:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def undo(self, current: QImage):
        """Вернуть предыдущий снимок, сохранив текущий в redo."""
        if not self._undo_stack:
            return None
        self._redo_stack.append(current.copy())
        return self._undo_stack.pop()

    def redo(self, current: QImage):
        if not self._redo_stack:
            return None
        self._undo_stack.append(current.copy())
        return self._redo_stack.pop()