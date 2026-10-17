"""Холст для пиксельного рисования."""

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QImage, QPainter, QColor, QPen
from PySide6.QtCore import Qt, QPoint, Signal

from src.history import History


class Canvas(QWidget):
    """Виджет, отображающий изображение и позволяющий рисовать пиксели."""

    cursor_moved = Signal(int, int)
    zoom_changed = Signal(int)
    color_picked = Signal(QColor, str)
    modified = Signal()          # холст изменился (для undo/redo кнопок)

    def __init__(self, width: int = 64, height: int = 64, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(200, 200)

        self._image = QImage(width, height, QImage.Format.Format_ARGB32)
        self._image.fill(QColor(255, 255, 255))

        self._zoom = 8
        self._offset = QPoint(0, 0)
        self._grid_visible = True

        self._primary_color = QColor(0, 0, 0)
        self._secondary_color = QColor(255, 255, 255)

        self._tool = None
        self._tool_active = False

        self._panning = False
        self._pan_start = QPoint(0, 0)
        self._offset_start = QPoint(0, 0)

        self._history = History(limit=50)

    # -------------- инструменты --------------
    def set_tool(self, tool):
        self._tool = tool

    def tool(self):
        return self._tool

    # -------------- публичный API --------------
    def image(self) -> QImage:
        return self._image

    def set_image(self, image: QImage):
        self._image = image
        self._history.clear()
        self._center_image()
        self.update()
        self.modified.emit()

    def new_image(self, width: int, height: int):
        self._image = QImage(width, height, QImage.Format.Format_ARGB32)
        self._image.fill(QColor(255, 255, 255))
        self._history.clear()
        self._center_image()
        self.update()
        self.modified.emit()

    def zoom(self) -> int:
        return self._zoom

    def set_zoom(self, value: int):
        new_zoom = max(1, min(64, int(value)))
        if new_zoom == self._zoom:
            return
        self._zoom = new_zoom
        self._center_image()
        self.update()
        self.zoom_changed.emit(self._zoom)

    def zoom_in(self):
        self.set_zoom(self._zoom + 1)

    def zoom_out(self):
        self.set_zoom(self._zoom - 1)

    def primary_color(self) -> QColor:
        return QColor(self._primary_color)

    def set_primary_color(self, color: QColor):
        self._primary_color = QColor(color)

    def secondary_color(self) -> QColor:
        return QColor(self._secondary_color)

    def set_secondary_color(self, color: QColor):
        self._secondary_color = QColor(color)

    def toggle_grid(self):
        self._grid_visible = not self._grid_visible
        self.update()

    def grid_visible(self) -> bool:
        return self._grid_visible

    def center_view(self):
        self._center_image()
        self.update()

    # -------------- история --------------
    def push_history(self):
        """Сохранить текущее состояние в историю (перед изменением)."""
        self._history.push(self._image)

    def can_undo(self) -> bool:
        return self._history.can_undo()

    def can_redo(self) -> bool:
        return self._history.can_redo()

    def undo(self):
        prev = self._history.undo(self._image)
        if prev is None:
            return
        self._image = prev
        self.update()
        self.modified.emit()

    def redo(self):
        nxt = self._history.redo(self._image)
        if nxt is None:
            return
        self._image = nxt
        self.update()
        self.modified.emit()

    # -------------- пиксели --------------
    def set_pixel(self, x: int, y: int, color: QColor):
        if not self._is_inside(x, y):
            return
        self._image.setPixelColor(x, y, color)
        self.update()

    def get_pixel(self, x: int, y: int) -> QColor:
        if not self._is_inside(x, y):
            return QColor(0, 0, 0, 0)
        return self._image.pixelColor(x, y)

    def draw_line_pixels(self, start, end, color: QColor):
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        while True:
            if self._is_inside(x0, y0):
                self._image.setPixelColor(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

        self.update()

    def flood_fill(self, x: int, y: int, color: QColor):
        if not self._is_inside(x, y):
            return
        target = self._image.pixelColor(x, y)
        if target.rgba() == color.rgba():
            return

        w = self._image.width()
        h = self._image.height()
        target_rgba = target.rgba()

        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if cx < 0 or cy < 0 or cx >= w or cy >= h:
                continue
            if self._image.pixelColor(cx, cy).rgba() != target_rgba:
                continue
            self._image.setPixelColor(cx, cy, color)
            stack.append((cx + 1, cy))
            stack.append((cx - 1, cy))
            stack.append((cx, cy + 1))
            stack.append((cx, cy - 1))

        self.update()

    # -------------- геометрия --------------
    def _widget_to_pixel(self, pos: QPoint) -> tuple[int, int]:
        x = (pos.x() - self._offset.x()) // self._zoom
        y = (pos.y() - self._offset.y()) // self._zoom
        return int(x), int(y)

    def _is_inside(self, x: int, y: int) -> bool:
        return 0 <= x < self._image.width() and 0 <= y < self._image.height()

    def _center_image(self):
        w = self._image.width() * self._zoom
        h = self._image.height() * self._zoom
        self._offset = QPoint(
            max(0, (self.width() - w) // 2),
            max(0, (self.height() - h) // 2),
        )

    # -------------- события --------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._center_image()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(40, 40, 40))

        target_w = self._image.width() * self._zoom
        target_h = self._image.height() * self._zoom

        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)

        scaled = self._image.scaled(
            target_w,
            target_h,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        painter.drawImage(self._offset, scaled)

        if self._grid_visible and self._zoom >= 6:
            painter.setPen(QPen(QColor(0, 0, 0, 60), 1))
            for x in range(self._image.width() + 1):
                px = self._offset.x() + x * self._zoom
                painter.drawLine(px, self._offset.y(), px, self._offset.y() + target_h)
            for y in range(self._image.height() + 1):
                py = self._offset.y() + y * self._zoom
                painter.drawLine(self._offset.x(), py, self._offset.x() + target_w, py)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        elif delta < 0:
            self.zoom_out()
        event.accept()

    def mousePressEvent(self, event):
        pos = event.position().toPoint()

        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = pos
            self._offset_start = QPoint(self._offset)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        if self._tool is None:
            return

        x, y = self._widget_to_pixel(pos)
        if self._is_inside(x, y):
            # Снимок для undo — ДО изменения
            self._history.push(self._image)
            self._tool_active = True
            self._tool.mouse_press(self, x, y, event.button())
            self.modified.emit()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()

        if self._panning:
            delta = pos - self._pan_start
            self._offset = self._offset_start + delta
            self.update()
            return

        x, y = self._widget_to_pixel(pos)
        if self._is_inside(x, y):
            self.cursor_moved.emit(x, y)

        if self._tool is not None and self._tool_active and self._is_inside(x, y):
            self._tool.mouse_move(self, x, y)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.unsetCursor()
            event.accept()
            return

        if self._tool is not None and self._tool_active:
            pos = event.position().toPoint()
            x, y = self._widget_to_pixel(pos)
            self._tool.mouse_release(self, x, y, event.button())
            self._tool_active = False