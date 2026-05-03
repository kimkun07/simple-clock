import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon


def _asset_path(filename: str) -> str:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.join(os.path.dirname(__file__), "..")
    return os.path.normpath(os.path.join(base, "assets", filename))


class SystemTray(QSystemTrayIcon):
    def __init__(self, window, move_controller, parent=None):
        icon = QIcon(_asset_path("icon.ico"))
        super().__init__(icon, parent)
        self._move_controller = move_controller
        self._build_menu()
        self.show()

    def _build_menu(self):
        menu = QMenu()
        menu.addAction("창 이동", self._move_controller.start)
        menu.addAction("커스터마이즈", self._on_customize)
        menu.addSeparator()
        menu.addAction("종료", QApplication.quit)
        self.setContextMenu(menu)

    def _on_customize(self):
        QMessageBox.information(
            None,
            "커스터마이즈",
            "커스터마이즈 기능은 Phase 3에서 구현됩니다.",
        )
