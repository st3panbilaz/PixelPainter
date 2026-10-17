"""Точка входа в приложение PixelPainter."""

import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.main_window import MainWindow
from src.new_image_dialog import NewImageDialog


# Абсолютный путь до иконки
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_PATH = os.path.join(APP_DIR, "assets", "icons", "pixelpainter.png")


def _load_app_icon() -> QIcon:
    if os.path.exists(ICON_PATH):
        return QIcon(ICON_PATH)
    return QIcon()


def run() -> int:
    """Запускает приложение и возвращает код выхода."""
    app = QApplication(sys.argv)
    app.setApplicationName("PixelPainter")
    app.setOrganizationName("PixelPainter")
    app.setDesktopFileName("pixelpainter")   # для Linux — связка с .desktop файлом
    app.setApplicationDisplayName("PixelPainter")

    icon = _load_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)

    dialog = NewImageDialog()
    if dialog.exec() != NewImageDialog.DialogCode.Accepted:
        return 0

    width, height = dialog.selected_size()

    window = MainWindow(initial_width=width, initial_height=height)
    if not icon.isNull():
        window.setWindowIcon(icon)
    window.show()

    return app.exec()