"""Палитра цветов и индикатор основного/второго цвета."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QColorDialog,
    QSizePolicy,
)
from PySide6.QtGui import QColor, QPainter, QBrush, QPen
from PySide6.QtCore import Qt, Signal


PALETTE_COLORS = [
    "#000000", "#1D2B53", "#7E2553", "#008751",
    "#AB5236", "#5F574F", "#C2C3C7", "#FFF1E8",
    "#FF004D", "#FFA300", "#FFEC27", "#00E436",
    "#29ADFF", "#83769C", "#FF77A8", "#FFCCAA",
]


class ColorSwatch(QPushButton):
    """Квадратик-кнопка с одним цветом."""

    left_clicked = Signal(QColor)
    right_clicked = Signal(QColor)

    def __init__(self, color: QColor, size: int = 22, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedSize(size, size)
        self.setToolTip(self._color.name().upper())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"QPushButton {{ background-color: {self._color.name()}; "
            f"border: 1px solid #222; }}"
        )

    def color(self) -> QColor:
        return QColor(self._color)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.left_clicked.emit(self._color)
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit(self._color)


class CurrentColorsWidget(QWidget):
    """Два квадратика: основной и второй цвет. Клик — открыть выбор цвета."""

    primary_clicked = Signal()
    secondary_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._primary = QColor(0, 0, 0)
        self._secondary = QColor(255, 255, 255)

        # Область основного и второго (в пикселях виджета)
        self._size = 28
        self._p1_rect = None
        self._p2_rect = None

    def set_primary(self, color: QColor):
        self._primary = QColor(color)
        self.update()

    def set_secondary(self, color: QColor):
        self._secondary = QColor(color)
        self.update()

    def _compute_rects(self):
        size = self._size
        x1 = (self.width() - size * 2) // 2
        y1 = (self.height() - size * 2) // 2
        x2 = x1 + 14
        y2 = y1 + 14
        self._p1_rect = (x1, y1, size, size)
        self._p2_rect = (x2, y2, size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self._compute_rects()

        # Вторичный — сзади
        x2, y2, s2, _ = self._p2_rect
        painter.setBrush(QBrush(self._secondary))
        painter.setPen(QPen(QColor(30, 30, 30), 1))
        painter.drawRect(x2, y2, s2, s2)

        # Основной — спереди
        x1, y1, s1, _ = self._p1_rect
        painter.setBrush(QBrush(self._primary))
        painter.drawRect(x1, y1, s1, s1)

    def mousePressEvent(self, event):
        if self._p1_rect is None:
            self._compute_rects()

        x = event.position().x()
        y = event.position().y()
        x1, y1, s1, _ = self._p1_rect
        x2, y2, s2, _ = self._p2_rect

        in_primary = x1 <= x <= x1 + s1 and y1 <= y <= y1 + s1
        in_secondary = x2 <= x <= x2 + s2 and y2 <= y <= y2 + s2

        if in_primary:
            self.primary_clicked.emit()
        elif in_secondary:
            self.secondary_clicked.emit()


class PaletteWidget(QWidget):
    """Панель с палитрой и индикатором текущих цветов."""

    primary_changed = Signal(QColor)
    secondary_changed = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._primary = QColor(0, 0, 0)
        self._secondary = QColor(255, 255, 255)

        self.current_colors = CurrentColorsWidget()
        self.current_colors.primary_clicked.connect(self._on_pick_primary)
        self.current_colors.secondary_clicked.connect(self._on_pick_secondary)

        # --- сетка цветов ---
        grid = QGridLayout()
        grid.setSpacing(2)
        grid.setContentsMargins(0, 0, 0, 0)

        columns = 4
        for i, hex_color in enumerate(PALETTE_COLORS):
            swatch = ColorSwatch(QColor(hex_color))
            swatch.left_clicked.connect(self._on_left)
            swatch.right_clicked.connect(self._on_right)
            row = i // columns
            col = i % columns
            grid.addWidget(swatch, row, col)

        # --- кнопки ---
        btn_swap = QPushButton("⇄ Поменять")
        btn_swap.clicked.connect(self._swap)

        btn_clear = QPushButton("Сбросить")
        btn_clear.clicked.connect(self._reset)

        row_buttons = QHBoxLayout()
        row_buttons.addWidget(btn_swap)
        row_buttons.addWidget(btn_clear)

        hint = QLabel("ЛКМ — основной\nПКМ — второй\nКлик по квадратику — выбор цвета")
        hint.setStyleSheet("color: #888; font-size: 10px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setWordWrap(True)

        root = QVBoxLayout(self)
        root.addWidget(self.current_colors)
        root.addLayout(row_buttons)
        root.addLayout(grid)
        root.addWidget(hint)
        root.addStretch(1)

    # ---------- публичное ----------
    def primary(self) -> QColor:
        return QColor(self._primary)

    def secondary(self) -> QColor:
        return QColor(self._secondary)

    def set_primary(self, color: QColor):
        self._primary = QColor(color)
        self.current_colors.set_primary(self._primary)
        self.primary_changed.emit(self._primary)

    def set_secondary(self, color: QColor):
        self._secondary = QColor(color)
        self.current_colors.set_secondary(self._secondary)
        self.secondary_changed.emit(self._secondary)

    # ---------- слоты ----------
    def _on_left(self, color: QColor):
        self.set_primary(color)

    def _on_right(self, color: QColor):
        self.set_secondary(color)

    def _on_pick_primary(self):
        color = QColorDialog.getColor(self._primary, self, "Основной цвет")
        if color.isValid():
            self.set_primary(color)

    def _on_pick_secondary(self):
        color = QColorDialog.getColor(self._secondary, self, "Второй цвет")
        if color.isValid():
            self.set_secondary(color)

    def _swap(self):
        p, s = self._primary, self._secondary
        self._primary, self._secondary = s, p
        self.current_colors.set_primary(self._primary)
        self.current_colors.set_secondary(self._secondary)
        self.primary_changed.emit(self._primary)
        self.secondary_changed.emit(self._secondary)

    def _reset(self):
        self.set_primary(QColor(0, 0, 0))
        self.set_secondary(QColor(255, 255, 255))