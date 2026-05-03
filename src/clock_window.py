from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow

from src.win32_utils import apply_tool_window_style, set_caption_color

DEFAULT_CAPTION_COLOR = "#2B2B2B"


class ClockWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimpleClock")
        self.setMinimumSize(200, 100)
        self.setCentralWidget(QLabel("테스트"))

    def showEvent(self, event):
        super().showEvent(event)
        apply_tool_window_style(self)
        set_caption_color(self, DEFAULT_CAPTION_COLOR)

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()
