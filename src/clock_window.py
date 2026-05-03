from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QMainWindow

from src.win32_utils import apply_tool_window_style


class ClockWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setMinimumSize(200, 100)
        label = QLabel("테스트")
        self.setCentralWidget(label)

    def showEvent(self, event):
        super().showEvent(event)
        apply_tool_window_style(self)
