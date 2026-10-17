#!/usr/bin/env bash
# Сборка .deb пакета PixelPainter.
# Запуск из корня проекта:  bash scripts/build_deb.sh

set -e

APP_NAME="pixelpainter"
VERSION="1.0.0"
ARCH="amd64"
MAINTAINER="st3panblaz <st3panblaz@localhost>"
DESC="Пиксельный редактор для Linux"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# ---------- 1. PyInstaller ----------
echo "==> Сборка через PyInstaller..."
rm -rf build dist "${APP_NAME}.spec"
pyinstaller \
    --noconfirm \
    --windowed \
    --name "$APP_NAME" \
    --add-data "assets:assets" \
    --icon "assets/icons/pixelpainter.png" \
    main.py

# ---------- 2. Структура .deb ----------
echo "==> Подготовка структуры пакета..."
PKG="build/${APP_NAME}_${VERSION}_${ARCH}"
rm -rf "$PKG"
mkdir -p "$PKG/DEBIAN"
mkdir -p "$PKG/usr/bin"
mkdir -p "$PKG/usr/share/applications"
mkdir -p "$PKG/usr/share/icons/hicolor"

cp -r "dist/${APP_NAME}" "$PKG/usr/share/${APP_NAME}"

cat > "$PKG/usr/bin/${APP_NAME}" <<EOF
#!/bin/sh
exec /usr/share/${APP_NAME}/${APP_NAME} "\$@"
EOF
chmod +x "$PKG/usr/bin/${APP_NAME}"

cp "assets/pixelpainter.desktop" "$PKG/usr/share/applications/"
cp -r assets/icons/hicolor/* "$PKG/usr/share/icons/hicolor/"

# ---------- 3. DEBIAN/control ----------
SIZE_KB=$(du -sk "$PKG/usr" | cut -f1)

cat > "$PKG/DEBIAN/control" <<EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: graphics
Priority: optional
Architecture: ${ARCH}
Maintainer: ${MAINTAINER}
Installed-Size: ${SIZE_KB}
Depends: libc6, libxcb-cursor0 | libxcb-cursor1
Description: ${DESC}
EOF

# ---------- 4. Сборка .deb ----------
echo "==> Сборка .deb..."
dpkg-deb --root-owner-group --build "$PKG" "dist/${APP_NAME}_${VERSION}_${ARCH}.deb"

echo ""
echo "Готово: dist/${APP_NAME}_${VERSION}_${ARCH}.deb"
echo "Установка:  sudo dpkg -i dist/${APP_NAME}_${VERSION}_${ARCH}.deb"