"""Главное окно приложения PixelPainter."""

import os

from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QStatusBar,
    QMessageBox,
    QLabel,
    QDockWidget,
    QColorDialog,
    QFileDialog,
)
from PySide6.QtGui import QAction, QKeySequence, QColor
from PySide6.QtCore import Qt

from src.canvas import Canvas
from src.new_image_dialog import NewImageDialog
from src.palette import PaletteWidget
from src.tools_panel import ToolsPanel
from src.icons import icon_color_picker, icon_undo, icon_redo
from src import io_utils

from src.tools.pencil import PencilTool
from src.tools.eraser import EraserTool
from src.tools.fill import FillTool
from src.tools.eyedropper import EyedropperTool


class MainWindow(QMainWindow):
    """Главное окно: меню, верхний тулбар, инструменты слева, палитра справа."""

    def __init__(self, initial_width: int = 64, initial_height: int = 64):
        super().__init__()
        self.setWindowTitle("Без имени — PixelPainter")
        self.resize(1200, 750)

        self._initial_width = initial_width
        self._initial_height = initial_height
        self._current_path: str | None = None

        self._tools = {
            "pencil": PencilTool(),
            "eraser": EraserTool(),
            "fill": FillTool(),
            "eyedropper": EyedropperTool(),
        }

        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()
        self._create_central_widget()
        self._create_tools_dock()
        self._create_palette_dock()

        self._on_tool_changed("pencil")
        self._update_undo_redo_state()

    # ---------- действия ----------
    def _create_actions(self):
        self.action_new = QAction("&Новый", self)
        self.action_new.setShortcut(QKeySequence.StandardKey.New)
        self.action_new.triggered.connect(self._on_new)

        self.action_open = QAction("&Открыть…", self)
        self.action_open.setShortcut(QKeySequence.StandardKey.Open)
        self.action_open.triggered.connect(self._on_open)

        self.action_save = QAction("&Сохранить", self)
        self.action_save.setShortcut(QKeySequence.StandardKey.Save)
        self.action_save.triggered.connect(self._on_save)

        self.action_save_as = QAction("Сохранить &как…", self)
        self.action_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.action_save_as.triggered.connect(self._on_save_as)

        self.action_export = QAction("&Экспорт в PNG…", self)
        self.action_export.triggered.connect(self._on_export)

        self.action_quit = QAction("В&ыход", self)
        self.action_quit.setShortcut(QKeySequence.StandardKey.Quit)
        self.action_quit.triggered.connect(self.close)

        self.action_undo = QAction(icon_undo(28), "&Отменить", self)
        self.action_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.action_undo.triggered.connect(self._on_undo)

        self.action_redo = QAction(icon_redo(28), "&Повторить", self)
        self.action_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.action_redo.triggered.connect(self._on_redo)

        self.action_pick_color = QAction(icon_color_picker(28), "Выбрать цвет…", self)
        self.action_pick_color.setShortcut("C")
        self.action_pick_color.setToolTip("Выбрать произвольный цвет (C)")
        self.action_pick_color.triggered.connect(self._on_pick_color)

        self.action_zoom_in = QAction("&Приблизить", self)
        self.action_zoom_in.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.action_zoom_in.triggered.connect(self._on_zoom_in)

        self.action_zoom_out = QAction("&Отдалить", self)
        self.action_zoom_out.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.action_zoom_out.triggered.connect(self._on_zoom_out)

        self.action_center = QAction("&Центрировать", self)
        self.action_center.setShortcut("Ctrl+0")
        self.action_center.triggered.connect(self._on_center)

        self.action_grid = QAction("Показать &сетку", self)
        self.action_grid.setCheckable(True)
        self.action_grid.setChecked(True)
        self.action_grid.setShortcut("Ctrl+G")
        self.action_grid.triggered.connect(self._on_toggle_grid)

        self.action_about = QAction("О &программе", self)
        self.action_about.triggered.connect(self._on_about)

    # ---------- меню ----------
    def _create_menu(self):
        menubar = self.menuBar()

        menu_file = menubar.addMenu("&Файл")
        menu_file.addAction(self.action_new)
        menu_file.addAction(self.action_open)
        menu_file.addSeparator()
        menu_file.addAction(self.action_save)
        menu_file.addAction(self.action_save_as)
        menu_file.addSeparator()
        menu_file.addAction(self.action_export)
        menu_file.addSeparator()
        menu_file.addAction(self.action_quit)

        menu_edit = menubar.addMenu("&Правка")
        menu_edit.addAction(self.action_undo)
        menu_edit.addAction(self.action_redo)
        menu_edit.addSeparator()
        menu_edit.addAction(self.action_pick_color)

        menu_view = menubar.addMenu("&Вид")
        menu_view.addAction(self.action_zoom_in)
        menu_view.addAction(self.action_zoom_out)
        menu_view.addAction(self.action_center)
        menu_view.addSeparator()
        menu_view.addAction(self.action_grid)

        menu_help = menubar.addMenu("&Справка")
        menu_help.addAction(self.action_about)

    # ---------- панель инструментов ----------
    def _create_toolbar(self):
        toolbar = QToolBar("Панель", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_open)
        toolbar.addAction(self.action_save)
        toolbar.addSeparator()
        toolbar.addAction(self.action_undo)
        toolbar.addAction(self.action_redo)
        toolbar.addSeparator()
        toolbar.addAction(self.action_pick_color)
        toolbar.addSeparator()
        toolbar.addAction(self.action_zoom_in)
        toolbar.addAction(self.action_zoom_out)
        toolbar.addAction(self.action_center)
        toolbar.addAction(self.action_grid)

        self.toolbar = toolbar

    # ---------- статус-бар ----------
    def _create_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Готово")

        self.coord_label = QLabel("—, —")
        self.coord_label.setMinimumWidth(90)
        self.coord_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.status.addPermanentWidget(self.coord_label)

    # ---------- центральная область ----------
    def _create_central_widget(self):
        self.canvas = Canvas(width=self._initial_width, height=self._initial_height)
        self.canvas.cursor_moved.connect(self._on_cursor_moved)
        self.canvas.zoom_changed.connect(self._on_zoom_changed)
        self.canvas.color_picked.connect(self._on_color_picked)
        self.canvas.modified.connect(self._update_undo_redo_state)
        self.setCentralWidget(self.canvas)
        self.status.showMessage(
            f"Холст {self._initial_width} × {self._initial_height}", 4000
        )

    # ---------- док слева ----------
    def _create_tools_dock(self):
        self.tools_panel = ToolsPanel()

        dock = QDockWidget("Инструменты", self)
        dock.setWidget(self.tools_panel)
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        self.tools_panel.tool_changed.connect(self._on_tool_changed)
        self.tools_dock = dock

    # ---------- док справа ----------
    def _create_palette_dock(self):
        self.palette = PaletteWidget()

        dock = QDockWidget("Цвета", self)
        dock.setWidget(self.palette)
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

        self.palette.primary_changed.connect(self.canvas.set_primary_color)
        self.palette.secondary_changed.connect(self.canvas.set_secondary_color)

        self.canvas.set_primary_color(self.palette.primary())
        self.canvas.set_secondary_color(self.palette.secondary())

        self.palette_dock = dock

    # ---------- обработчики ----------
    def _on_cursor_moved(self, x: int, y: int):
        self.coord_label.setText(f"x: {x}, y: {y}")

    def _on_zoom_changed(self, zoom: int):
        self.status.showMessage(f"Зум: {zoom}x", 2000)

    def _on_zoom_in(self):
        self.canvas.zoom_in()

    def _on_zoom_out(self):
        self.canvas.zoom_out()

    def _on_center(self):
        self.canvas.center_view()

    def _on_toggle_grid(self):
        self.canvas.toggle_grid()

    def _on_tool_changed(self, tool_id: str):
        tool = self._tools.get(tool_id)
        if tool is None:
            return
        self.canvas.set_tool(tool)
        self.status.showMessage(f"Инструмент: {tool.name}", 2000)

    def _on_color_picked(self, color: QColor, target: str):
        if target == "secondary":
            self.palette.set_secondary(color)
        else:
            self.palette.set_primary(color)

    def _on_pick_color(self):
        color = QColorDialog.getColor(self.canvas.primary_color(), self, "Выбрать цвет")
        if color.isValid():
            self.palette.set_primary(color)

    def _on_undo(self):
        self.canvas.undo()
        self._update_undo_redo_state()
        self.status.showMessage("Отменено", 1500)

    def _on_redo(self):
        self.canvas.redo()
        self._update_undo_redo_state()
        self.status.showMessage("Повторено", 1500)

    def _update_undo_redo_state(self):
        self.action_undo.setEnabled(self.canvas.can_undo())
        self.action_redo.setEnabled(self.canvas.can_redo())

    # ---------- ФАЙЛ: НОВЫЙ ----------
    def _on_new(self):
        dialog = NewImageDialog(
            self,
            default_w=self.canvas.image().width(),
            default_h=self.canvas.image().height(),
        )
        if dialog.exec() != NewImageDialog.DialogCode.Accepted:
            return
        w, h = dialog.selected_size()
        self.canvas.new_image(w, h)
        self._current_path = None
        self._update_title()
        self._update_undo_redo_state()
        self.status.showMessage(f"Новый холст {w} × {h}", 3000)

    # ---------- ФАЙЛ: ОТКРЫТЬ ----------
    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение", "", io_utils.OPEN_FILTER
        )
        if not path:
            return
        try:
            qimg = io_utils.load_image(path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{e}")
            return

        self.canvas.set_image(qimg)
        self._current_path = path
        self._update_title()
        self._update_undo_redo_state()
        self.status.showMessage(f"Открыт: {os.path.basename(path)}", 3000)

    # ---------- ФАЙЛ: СОХРАНИТЬ ----------
    def _on_save(self):
        if self._current_path is None:
            self._on_save_as()
            return
        self._save_to(self._current_path)

    def _on_save_as(self):
        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Сохранить как",
            self._current_path or "image.png",
            io_utils.SAVE_FILTER,
        )
        if not path:
            return

        # Если пользователь не ввёл расширение — подставим по фильтру
        if not os.path.splitext(path)[1]:
            ext = ".png"
            if "BMP" in selected_filter:
                ext = ".bmp"
            elif "JPEG" in selected_filter:
                ext = ".jpg"
            elif "WebP" in selected_filter:
                ext = ".webp"
            elif "GIF" in selected_filter:
                ext = ".gif"
            path += ext

        self._save_to(path)

    def _save_to(self, path: str):
        try:
            io_utils.save_image(self.canvas.image(), path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")
            return

        self._current_path = path
        self._update_title()
        self.status.showMessage(f"Сохранено: {os.path.basename(path)}", 3000)

    # ---------- ФАЙЛ: ЭКСПОРТ ----------
    def _on_export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в PNG", "export.png", "PNG (*.png)"
        )
        if not path:
            return
        if not os.path.splitext(path)[1]:
            path += ".png"
        try:
            io_utils.save_image(self.canvas.image(), path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать:\n{e}")
            return
        self.status.showMessage(f"Экспортировано: {os.path.basename(path)}", 3000)

    # ---------- заголовок ----------
    def _update_title(self):
        if self._current_path:
            name = os.path.basename(self._current_path)
            self.setWindowTitle(f"{name} — PixelPainter")
        else:
            self.setWindowTitle("Без имени — PixelPainter")

    def _on_about(self):
        QMessageBox.about(
            self,
            "О программе",
            "<b>PixelPainter</b><br>"
            "Пиксельный редактор для Linux.<br><br>"
            "Сделан на PySide6 и Pillow.",
        )