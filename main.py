import os
import sys
import traceback
from datetime import datetime

from PyQt6.QtCore import QSharedMemory
from PyQt6.QtWidgets import QApplication

from src.clock_window import ClockWindow
from src.config import ConfigStore


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


def main():
    _install_excepthook()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    shared_mem = QSharedMemory("SimpleClock-singleton")
    if shared_mem.attach():
        sys.exit(0)
    shared_mem.create(1)

    config = ConfigStore.load()
    window = ClockWindow(config)
    def _on_quit():
        window.sync_window_geometry()
        config.save()

    app.aboutToQuit.connect(_on_quit)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
