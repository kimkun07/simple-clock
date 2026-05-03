from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget

from src.config import ConfigStore, _make_default_textbox
from src.textbox import TextBoxWidget
from src.win32_utils import set_caption_color


class ClockWindow(QMainWindow):
    def __init__(self, config: ConfigStore):
        super().__init__()
        self._config = config
        self._textboxes: list[TextBoxWidget] = []

        self.setWindowTitle("SimpleClock")

        self._container = QWidget()
        self.setCentralWidget(self._container)

        self._apply_window_config()
        self._rebuild_textboxes()
        self._schedule_tick()

    def _apply_window_config(self) -> None:
        w = self._config.window
        self.move(w.get("x", 100), w.get("y", 100))
        self.resize(w.get("width", 420), w.get("height", 160))
        if w.get("always_on_top", False):
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._container.setStyleSheet(
            f"background-color: {w.get('background_color', '#1e1e1e')};"
        )

    def showEvent(self, event):
        super().showEvent(event)
        set_caption_color(self, self._config.window.get("titlebar_color", "#2b2b2b"))

    def _rebuild_textboxes(self) -> None:
        for tb in self._textboxes:
            tb.deleteLater()
        self._textboxes.clear()
        for tb_cfg in self._config.textboxes:
            tb = TextBoxWidget(tb_cfg, parent=self._container)
            tb.show()
            self._textboxes.append(tb)

    def _schedule_tick(self) -> None:
        now = datetime.now()
        for tb in self._textboxes:
            tb.tick(now)
        delay_ms = 1000 - (now.microsecond // 1000)
        QTimer.singleShot(delay_ms, self._schedule_tick)

    # --- Public API for CustomizeDialog ---

    def set_background_color(self, color_hex: str) -> None:
        self._config.window["background_color"] = color_hex
        self._container.setStyleSheet(f"background-color: {color_hex};")

    def set_titlebar_color(self, color_hex: str) -> None:
        self._config.window["titlebar_color"] = color_hex
        set_caption_color(self, color_hex)

    def set_always_on_top(self, value: bool) -> None:
        self._config.window["always_on_top"] = value
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, value)
        self.show()

    def add_textbox(self, tb_cfg: dict) -> TextBoxWidget:
        self._config.textboxes.append(tb_cfg)
        tb = TextBoxWidget(tb_cfg, parent=self._container)
        tb.show()
        self._textboxes.append(tb)
        return tb

    def remove_textbox(self, textbox_id: str) -> None:
        for tb in list(self._textboxes):
            if tb.textbox_id == textbox_id:
                tb.deleteLater()
                self._textboxes.remove(tb)
                break
        self._config.textboxes[:] = [
            t for t in self._config.textboxes if t.get("id") != textbox_id
        ]

    def update_textbox(self, textbox_id: str, updates: dict) -> None:
        for tb in self._textboxes:
            if tb.textbox_id == textbox_id:
                tb.update_config(updates)
                break
        for t in self._config.textboxes:
            if t.get("id") == textbox_id:
                t.update(updates)
                break

    def sync_window_geometry(self) -> None:
        geo = self.geometry()
        self._config.window.update(
            {"x": geo.x(), "y": geo.y(), "width": geo.width(), "height": geo.height()}
        )
        for tb in self._textboxes:
            cfg = tb.get_config()
            for t in self._config.textboxes:
                if t.get("id") == cfg["id"]:
                    t.update(cfg)
                    break

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()
