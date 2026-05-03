from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow


class ClockWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimpleClock")
        self.setCentralWidget(QLabel("테스트"))

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()
