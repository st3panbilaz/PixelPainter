"""Генерация всех размеров иконки из большой PNG.

Запускать из корня проекта:
    python scripts/generate_icons.py
"""

import os
from PIL import Image


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "assets", "icons", "pixelpainter.png")
OUTPUT_ROOT = os.path.join(ROOT, "assets", "icons", "hicolor")

SIZES = [16, 22, 24, 32, 48, 64, 128, 256, 512]


def main():
    if not os.path.exists(SOURCE):
        print(f"ОШИБКА: не найден файл-источник: {SOURCE}")
        print("Положи pixelpainter.png в assets/icons/")
        return

    img = Image.open(SOURCE).convert("RGBA")
    print(f"Источник: {SOURCE} — {img.width}x{img.height}")

    for size in SIZES:
        out_dir = os.path.join(OUTPUT_ROOT, f"{size}x{size}", "apps")
        os.makedirs(out_dir, exist_ok=True)

        resized = img.resize((size, size), Image.LANCZOS)
        out_path = os.path.join(out_dir, "pixelpainter.png")
        resized.save(out_path, "PNG")
        print(f"  {size}x{size} → {out_path}")

    print("\nГотово.")


if __name__ == "__main__":
    main()