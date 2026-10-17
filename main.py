"""Запуск PixelPainter."""

import sys
import os

# Добавляем корень проекта в sys.path, чтобы импорт src.* работал
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import run


if __name__ == "__main__":
    sys.exit(run())