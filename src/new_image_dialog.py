"""Диалог создания нового изображения."""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QSpinBox,
    QComboBox,
    QDialogButtonBox,
    QLabel,
)
from PySide6.QtCore import Qt


# Пресеты: (подпись, ширина, высота). Ширина/высота = None для «Свой размер»
PRESETS = [
    ("Свой размер", None, None),
    ("16 × 16", 16, 16),
    ("32 × 32", 32, 32),
    ("64 × 64", 64, 64),
    ("128 × 128", 128, 128),
    ("256 × 256", 256, 256),
    ("512 × 512", 512, 512),
]


class NewImageDialog(QDialog):
    """Диалог выбора размера нового холста."""

    def __init__(self, parent=None, default_w: int = 64, default_h: int = 64):
        super().__init__(parent)
        self.setWindowTitle("Новое изображение")
        self.setModal(True)
        self.setMinimumWidth(320)

        # --- элементы ---
        self.preset_combo = QComboBox()
        for label, _, _ in PRESETS:
            self.preset_combo.addItem(label)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 4096)
        self.width_spin.setValue(default_w)
        self.width_spin.setSuffix(" px")

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 4096)
        self.height_spin.setValue(default_h)
        self.height_spin.setSuffix(" px")

        # --- layout ---
        form = QFormLayout()
        form.addRow("Пресет:", self.preset_combo)
        form.addRow("Ширина:", self.width_spin)
        form.addRow("Высота:", self.height_spin)

        hint = QLabel("Пиксели квадратные, размер можно поменять позже.")
        hint.setStyleSheet("color: #888;")
        hint.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Создать")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(hint)
        root.addSpacing(6)
        root.addWidget(buttons)

        # --- связи ---
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        # Ставим пресет, совпадающий с default (если есть)
        for i, (_, w, h) in enumerate(PRESETS):
            if w == default_w and h == default_h:
                self.preset_combo.setCurrentIndex(i)
                break

    def _on_preset_changed(self, index: int):
        _, w, h = PRESETS[index]
        if w is None or h is None:
            return  # «Свой размер» — не трогаем
        self.width_spin.setValue(w)
        self.height_spin.setValue(h)

    def selected_size(self) -> tuple[int, int]:
        return self.width_spin.value(), self.height_spin.value()