from PyQt6.QtCore import QEvent, QObject, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QApplication


class MoveModeController(QObject):
    geometryCommitted = pyqtSignal()

    def __init__(self, window: QObject):
        super().__init__()
        self._window = window
        self._active = False
        self._original_geometry = None
        self._start_cursor = None
        self._start_window_pos = None

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(16)
        self._poll_timer.timeout.connect(self._poll_position)

        self._deadman = QTimer(self)
        self._deadman.setSingleShot(True)
        self._deadman.setInterval(30_000)
        self._deadman.timeout.connect(self._cancel)

    def start(self):
        if self._active:
            return
        self._active = True
        self._original_geometry = self._window.geometry()
        self._start_cursor = QCursor.pos()
        self._start_window_pos = self._window.pos()
        QApplication.setOverrideCursor(Qt.CursorShape.SizeAllCursor)
        QApplication.instance().installEventFilter(self)
        self._poll_timer.start()
        self._deadman.start()

    def _poll_position(self):
        delta = QCursor.pos() - self._start_cursor
        self._window.move(self._start_window_pos + delta)

    def _commit(self):
        if not self._active:
            return
        self._active = False
        self._poll_timer.stop()
        self._deadman.stop()
        QApplication.restoreOverrideCursor()
        QApplication.instance().removeEventFilter(self)
        self.geometryCommitted.emit()

    def _cancel(self):
        if not self._active:
            return
        self._active = False
        self._poll_timer.stop()
        self._deadman.stop()
        QApplication.restoreOverrideCursor()
        QApplication.instance().removeEventFilter(self)
        self._window.setGeometry(self._original_geometry)

    def eventFilter(self, obj, event):
        if not self._active:
            return False
        t = event.type()
        if t == QEvent.Type.MouseButtonPress:
            self._commit()
            return True
        if t == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            self._cancel()
            return True
        return False
