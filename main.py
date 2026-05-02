import os
import sys
import traceback
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow


def _install_excepthook():
    log_dir = os.path.join(os.environ.get("APPDATA", ""), "SimpleClock")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "error.log")

    def _hook(exc_type, exc_value, exc_tb):
        timestamp = datetime.now().isoformat(timespec="seconds")
        lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}]\n")
            f.writelines(lines)
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = _hook


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimpleClock")
        self.setMinimumSize(200, 100)
        label = QLabel("테스트")
        label.setAlignment(label.alignment())
        self.setCentralWidget(label)


def main():
    _install_excepthook()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
