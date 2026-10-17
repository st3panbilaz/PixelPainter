"""Утилиты сохранения и загрузки изображений через Pillow."""

import os

from PIL import Image
from PySide6.QtGui import QImage
from PySide6.QtCore import QBuffer, QIODevice


# Расширения, которые умеем и открывать, и сохранять
SUPPORTED_EXTENSIONS = [".png", ".bmp", ".jpg", ".jpeg", ".webp", ".gif"]

# Человекочитаемые фильтры для диалогов
OPEN_FILTER = (
    "Изображения (*.png *.bmp *.jpg *.jpeg *.webp *.gif);;"
    "PNG (*.png);;"
    "BMP (*.bmp);;"
    "JPEG (*.jpg *.jpeg);;"
    "WebP (*.webp);;"
    "GIF (*.gif);;"
    "Все файлы (*)"
)

SAVE_FILTER = (
    "PNG (*.png);;"
    "BMP (*.bmp);;"
    "JPEG (*.jpg *.jpeg);;"
    "WebP (*.webp);;"
    "GIF (*.gif)"
)


def qimage_to_pil(qimg: QImage) -> Image.Image:
    """Конвертирует QImage в PIL.Image (RGBA)."""
    # Приводим формат к RGBA8888 — так надёжнее
    converted = qimg.convertToFormat(QImage.Format.Format_RGBA8888)

    width = converted.width()
    height = converted.height()
    ptr = converted.constBits()
    # PySide6 отдаёт memoryview — оборачиваем в bytes
    data = bytes(ptr)

    return Image.frombytes("RGBA", (width, height), data, "raw", "RGBA", 0, 1)


def pil_to_qimage(pil_img: Image.Image) -> QImage:
    """Конвертирует PIL.Image в QImage (RGBA8888)."""
    if pil_img.mode != "RGBA":
        pil_img = pil_img.convert("RGBA")

    data = pil_img.tobytes("raw", "RGBA")
    qimg = QImage(data, pil_img.width, pil_img.height,
                  QImage.Format.Format_RGBA8888)
    # Копируем, чтобы QImage владел памятью
    return qimg.copy()


def save_image(qimg: QImage, path: str) -> None:
    """Сохраняет QImage в файл по расширению. Формат определяет Pillow."""
    pil_img = qimage_to_pil(qimg)
    ext = os.path.splitext(path)[1].lower()

    # JPEG не поддерживает прозрачность — конвертируем в RGB
    if ext in (".jpg", ".jpeg"):
        # Белый фон вместо прозрачности
        bg = Image.new("RGB", pil_img.size, (255, 255, 255))
        bg.paste(pil_img, mask=pil_img.split()[3])
        pil_img = bg

    pil_img.save(path)


def load_image(path: str) -> QImage:
    """Загружает изображение из файла в QImage (RGBA)."""
    pil_img = Image.open(path)
    return pil_to_qimage(pil_img)