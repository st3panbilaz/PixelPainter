"""Левая панель с инструментами (вертикально)."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QToolButton,
    QButtonGroup,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QSize

from src.icons import (
    icon_pencil,
    icon_eraser,
    icon_fill,
    icon_eyedropper,
)


# (tool_id, подпись, фабрика иконки)
TOOLS = [
    ("pencil",     "Карандаш", icon_pencil),
    ("eraser",     "Ластик",   icon_eraser),
    ("fill",       "Заливка",  icon_fill),
    ("eyedropper", "Пипетка",  icon_eyedropper),
]


class ToolsPanel(QWidget):
    """Вертикальная панель с кнопками инструментов."""

    tool_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 4, 2, 4)
        layout.setSpacing(2)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons = {}

        for tool_id, name, icon_factory in TOOLS:
            btn = QToolButton()
            btn.setIcon(icon_factory(28))
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(name)
            btn.setCheckable(True)
            btn.setAutoRaise(True)
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda _=False, tid=tool_id: self._on_click(tid))

            self._group.addButton(btn)
            layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)
            self._buttons[tool_id] = btn

        layout.addStretch(1)

        # По умолчанию — карандаш
        self.set_current("pencil", emit=False)

    def _on_click(self, tool_id: str):
        self.tool_changed.emit(tool_id)

    def set_current(self, tool_id: str, emit: bool = True):
        btn = self._buttons.get(tool_id)
        if btn is None:
            return
        btn.setChecked(True)
        if emit:
            self.tool_changed.emit(tool_id)