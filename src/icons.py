"""Однотонные иконки инструментов (рисуются кодом)."""

from PySide6.QtGui import (
    QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPolygonF
)
from PySide6.QtCore import Qt, QPointF


# Единый цвет всех иконок
ICON_COLOR = QColor(40, 40, 40)


def _new_pixmap(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    return pm


def _make_pen(w: int, width_factor: float = 0.09) -> QPen:
    pen = QPen(ICON_COLOR, max(1.6, w * width_factor))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def icon_pencil(size: int = 32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    p.setPen(_make_pen(w))
    # Корпус карандаша — диагональная линия
    p.drawLine(w // 4, 3 * w // 4, 3 * w // 4, w // 4)
    # Кончик
    p.drawLine(w // 4, 3 * w // 4, w // 5, 4 * w // 5)
    p.end()
    return QIcon(pm)


def icon_eraser(size: int = 32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    p.setPen(_make_pen(w))
    p.setBrush(Qt.BrushStyle.NoBrush)
    # Наклонный прямоугольник (ластик)
    p.drawLine(w // 6, 5 * w // 6, 3 * w // 4, w // 5)         # верх-низ
    p.drawLine(w // 4, 5 * w // 6, 5 * w // 6, w // 3)         # низ-верх
    p.drawLine(w // 6, 5 * w // 6, w // 4, 5 * w // 6)         # нижняя сторона
    p.drawLine(3 * w // 4, w // 5, 5 * w // 6, w // 3)         # верхняя сторона
    # Разделительная линия
    p.drawLine(w // 3, 2 * w // 3, 2 * w // 3, w // 3)
    p.end()
    return QIcon(pm)


def icon_fill(size: int = 32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    p.setPen(_make_pen(w))
    p.setBrush(Qt.BrushStyle.NoBrush)
    # Ведро (перевёрнутый конус)
    p.drawLine(w // 4, w // 3, 3 * w // 4, w // 3)
    p.drawLine(w // 4, w // 3, w // 2, 2 * w // 3)
    p.drawLine(3 * w // 4, w // 3, w // 2, 2 * w // 3)
    # Капля
    p.drawLine(w // 2, 2 * w // 3, w // 2, 3 * w // 4)
    # Ручка
    p.drawLine(3 * w // 4, w // 3, 5 * w // 6, w // 5)
    p.end()
    return QIcon(pm)


def icon_eyedropper(size: int = 32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    p.setPen(_make_pen(w))
    p.setBrush(Qt.BrushStyle.NoBrush)
    # Диагональная палочка пипетки
    p.drawLine(w // 4, 3 * w // 4, 3 * w // 4, w // 4)
    # Головка
    p.drawLine(2 * w // 3, w // 6, 5 * w // 6, w // 3)
    p.drawLine(2 * w // 3, w // 6, 3 * w // 4, w // 4)
    p.drawLine(5 * w // 6, w // 3, 3 * w // 4, w // 4)
    # Кончик
    p.drawLine(w // 4, 3 * w // 4, w // 5, 4 * w // 5)
    p.end()
    return QIcon(pm)


def icon_color_picker(size: int = 32) -> QIcon:
    """Иконка выбора цвета — контур круга (тоже однотонная)."""
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    p.setPen(_make_pen(w, 0.075))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(w // 6, w // 6, 2 * w // 3, 2 * w // 3)
    # Маленькая точка в центре
    p.setBrush(QBrush(ICON_COLOR))
    p.drawEllipse(w // 2 - 2, w // 2 - 2, 4, 4)
    p.end()
    return QIcon(pm)


def icon_undo(size: int = 32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    p.setPen(_make_pen(w))
    p.setBrush(Qt.BrushStyle.NoBrush)
    # Дуга стрелки
    p.drawArc(w // 5, w // 3, 3 * w // 5, 3 * w // 5, 30 * 16, 180 * 16)
    # Наконечник
    p.drawLine(w // 5, 2 * w // 3, w // 4, w // 2)
    p.drawLine(w // 5, 2 * w // 3, w // 3, w // 2)
    p.end()
    return QIcon(pm)


def icon_redo(size: int = 32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    p.setPen(_make_pen(w))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(w // 5, w // 3, 3 * w // 5, 3 * w // 5, -30 * 16, -180 * 16)
    p.drawLine(4 * w // 5, 2 * w // 3, 3 * w // 4, w // 2)
    p.drawLine(4 * w // 5, 2 * w // 3, 2 * w // 3, w // 2)
    p.end()
    return QIcon(pm)