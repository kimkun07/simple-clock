import uuid
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QFrame, QTextEdit

from src.time_engine import render, remap_run


class TextBoxWidget(QTextEdit):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._id: str = config.get("id", str(uuid.uuid4()))
        self._template_text: str = config.get("template_text", "")
        self._format_runs: list[dict] = list(config.get("format_runs", []))
        self._base_font_family: str = config.get("base_font_family", "Segoe UI")
        self._base_font_size: int = config.get("base_font_size", 24)
        self._last_rendered: str | None = None
        self._ticking: bool = False

        self.setReadOnly(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFrameStyle(QFrame.Shape.NoFrame.value)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setStyleSheet("QTextEdit { background: transparent; border: none; }")

        self._apply_base_font()
        self.setGeometry(
            config.get("x", 0),
            config.get("y", 0),
            config.get("width", 200),
            60,  # initial placeholder; _fit_size will correct this after first render
        )
        self.document().documentLayout().documentSizeChanged.connect(
            lambda _size: self._fit_size()
        )

    def _fit_size(self) -> None:
        if self._ticking:
            return  # defer until end of tick to avoid mid-update resize flicker
        m = self.contentsMargins()
        new_w = max(int(self.document().idealWidth()) + m.left() + m.right(), 10)
        new_h = max(int(self.document().size().height()) + m.top() + m.bottom(), 10)
        if new_w != self.width() or new_h != self.height():
            self.resize(new_w, new_h)

    def _apply_base_font(self) -> None:
        self.document().setDefaultFont(QFont(self._base_font_family, self._base_font_size))

    def tick(self, now: datetime) -> None:
        rendered_text, offset_map = render(self._template_text, now)
        if rendered_text == self._last_rendered:
            return
        self._last_rendered = rendered_text
        self._ticking = True
        self.setUpdatesEnabled(False)
        self.setPlainText(rendered_text)
        self._apply_format_runs(offset_map)
        self._ticking = False
        self._fit_size()             # single resize after both steps
        self.setUpdatesEnabled(True)
        self.update()

    def _apply_format_runs(self, offset_map) -> None:
        doc = self.document()
        for run in self._format_runs:
            r_start, r_len = remap_run(run["start"], run["length"], offset_map)
            if r_len <= 0:
                continue
            cursor = QTextCursor(doc)
            cursor.setPosition(r_start)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                r_len,
            )
            fmt = QTextCharFormat()
            if run.get("color"):
                fmt.setForeground(QColor(run["color"]))
            fmt.setFontWeight(QFont.Weight.Bold if run.get("bold") else QFont.Weight.Normal)
            fmt.setFontItalic(bool(run.get("italic")))
            cursor.mergeCharFormat(fmt)

    def update_config(self, updates: dict) -> None:
        if "template_text" in updates:
            self._template_text = updates["template_text"]
        if "format_runs" in updates:
            self._format_runs = list(updates["format_runs"])
        font_changed = False
        if "base_font_family" in updates and updates["base_font_family"] != self._base_font_family:
            self._base_font_family = updates["base_font_family"]
            font_changed = True
        if "base_font_size" in updates and updates["base_font_size"] != self._base_font_size:
            self._base_font_size = updates["base_font_size"]
            font_changed = True
        if font_changed:
            self._apply_base_font()
        geo_keys = {"x", "y"}
        if geo_keys & updates.keys():
            self.setGeometry(
                updates.get("x", self.x()),
                updates.get("y", self.y()),
                self.width(),   # width is auto; never apply from config
                self.height(),  # height is auto; never apply from config
            )
        self._last_rendered = None  # force re-render on next tick

    def get_config(self) -> dict:
        return {
            "id": self._id,
            "x": self.x(),
            "y": self.y(),
            "width": self.width(),
            "height": self.height(),
            "template_text": self._template_text,
            "format_runs": list(self._format_runs),
            "base_font_family": self._base_font_family,
            "base_font_size": self._base_font_size,
        }

    @property
    def textbox_id(self) -> str:
        return self._id
