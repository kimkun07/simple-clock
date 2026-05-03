import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from src.config import ConfigStore
from src.customize_dialog import CustomizeDialog


def _asset_path(filename: str) -> str:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.join(os.path.dirname(__file__), "..")
    return os.path.normpath(os.path.join(base, "assets", filename))


class SystemTray(QSystemTrayIcon):
    def __init__(self, window, config: ConfigStore, parent=None):
        super().__init__(QIcon(_asset_path("icon.ico")), parent)
        self._window = window
        self._config = config
        self._dialog: CustomizeDialog | None = None
        self._build_menu()
        self.show()

    def _build_menu(self) -> None:
        menu = QMenu()
        menu.addAction("커스터마이즈", self._on_customize)
        menu.addSeparator()
        menu.addAction("종료", QApplication.quit)
        self.setContextMenu(menu)

    def _on_customize(self) -> None:
        if self._dialog is None or not self._dialog.isVisible():
            self._dialog = CustomizeDialog(self._window, self._config)
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()
