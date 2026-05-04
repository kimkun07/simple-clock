from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDialog,
    QFontComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.config import ConfigStore, _make_default_textbox


class _TemplateEditor(QTextEdit):
    """QTextEdit that tracks format_runs and emits template_changed on every edit."""

    template_changed = pyqtSignal(str, object)  # (template_text, format_runs)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._runs: list[dict] = []
        self._applying = False
        self.document().contentsChange.connect(self._on_contents_change)
        self.textChanged.connect(self._on_text_changed)

    def load(self, template_text: str, format_runs: list[dict]) -> None:
        self._applying = True
        self._runs = [dict(r) for r in format_runs]
        self.setPlainText(template_text)
        self._apply_runs_to_display()
        self._applying = False

    def _apply_runs_to_display(self) -> None:
        self._applying = True
        doc = self.document()
        text_len = len(self.toPlainText())
        for run in self._runs:
            start = run["start"]
            end = min(start + run["length"], text_len)
            if end <= start:
                continue
            cursor = QTextCursor(doc)
            cursor.setPosition(start)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                end - start,
            )
            fmt = QTextCharFormat()
            if run.get("color"):
                fmt.setForeground(QColor(run["color"]))
            fmt.setFontWeight(QFont.Weight.Bold if run.get("bold") else QFont.Weight.Normal)
            fmt.setFontItalic(bool(run.get("italic")))
            cursor.mergeCharFormat(fmt)
        self._applying = False

    def _on_contents_change(self, pos: int, removed: int, added: int) -> None:
        if self._applying:
            return
        new_runs = []
        for run in self._runs:
            r_start = run["start"]
            r_end = r_start + run["length"]
            if r_end <= pos:
                new_runs.append(run)
            elif r_start >= pos + removed:
                shifted = dict(run)
                shifted["start"] = r_start + added - removed
                new_runs.append(shifted)
            # runs overlapping the edited region are dropped
        self._runs = new_runs

    def _on_text_changed(self) -> None:
        if self._applying:
            return
        self.template_changed.emit(self.toPlainText(), list(self._runs))

    def apply_formatting(self, **kwargs) -> None:
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return
        start = cursor.selectionStart()
        length = cursor.selectionEnd() - start
        if length <= 0:
            return
        existing = next(
            (r for r in self._runs if r["start"] == start and r["length"] == length),
            None,
        )
        if existing:
            for key, val in kwargs.items():
                # Toggle bold/italic when the button is pressed again on the same selection
                if key in ("bold", "italic") and existing.get(key) == val:
                    existing[key] = False
                else:
                    existing[key] = val
        else:
            run = {"start": start, "length": length, "color": None, "bold": False, "italic": False}
            # Inherit bold/italic from any run that fully covers the selection so that
            # picking a color does not inadvertently strip existing bold/italic.
            sel_end = start + length
            for r in self._runs:
                if r["start"] <= start and r["start"] + r["length"] >= sel_end:
                    run["bold"] = r.get("bold", False)
                    run["italic"] = r.get("italic", False)
                    break
            run.update(kwargs)
            self._runs.append(run)
        self._apply_runs_to_display()
        self.template_changed.emit(self.toPlainText(), list(self._runs))

    def insert_variable(self, var: str) -> None:
        cursor = self.textCursor()
        cursor.insertText(var)
        # contentsChange handles run shifting


class CustomizeDialog(QDialog):
    def __init__(self, clock_window, config: ConfigStore, parent=None):
        super().__init__(parent)
        self._clock = clock_window
        self._config = config
        self._selected_id: str | None = None
        self._updating = False

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(200)
        self._save_timer.timeout.connect(self._config.save)

        self.setWindowTitle("커스터마이즈")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self._setup_ui()
        self._load_textbox_list()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: textbox list ──────────────────────────────────────────────
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("텍스트박스 목록"))
        self._list = QListWidget()
        self._list.currentItemChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self._list)

        btn_row = QHBoxLayout()
        self._add_btn = QPushButton("추가")
        self._del_btn = QPushButton("삭제")
        self._add_btn.clicked.connect(self._add_textbox)
        self._del_btn.clicked.connect(self._delete_textbox)
        btn_row.addWidget(self._add_btn)
        btn_row.addWidget(self._del_btn)
        left_layout.addLayout(btn_row)
        splitter.addWidget(left)

        # ── Right: editor ───────────────────────────────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)

        # Formatting toolbar
        toolbar = QHBoxLayout()
        self._bold_btn = QPushButton("B")
        bold_font = QFont()
        bold_font.setBold(True)
        self._bold_btn.setFont(bold_font)
        self._italic_btn = QPushButton("I")
        italic_font = QFont()
        italic_font.setItalic(True)
        self._italic_btn.setFont(italic_font)
        self._color_btn = QPushButton("색상")
        self._bold_btn.clicked.connect(lambda: self._editor.apply_formatting(bold=True))
        self._italic_btn.clicked.connect(lambda: self._editor.apply_formatting(italic=True))
        self._color_btn.clicked.connect(self._pick_text_color)
        toolbar.addWidget(self._bold_btn)
        toolbar.addWidget(self._italic_btn)
        toolbar.addWidget(self._color_btn)
        toolbar.addStretch()
        right_layout.addLayout(toolbar)

        # Variable buttons — row 1: zero-padded originals
        var_row1 = QHBoxLayout()
        for var in ["{HH}", "{mm}", "{ss}", "{YYYY}", "{MM}", "{DD}", "{ddd}"]:
            btn = QPushButton(var)
            btn.setFixedWidth(62)
            btn.clicked.connect(lambda _checked, v=var: self._editor.insert_variable(v))
            var_row1.addWidget(btn)
        var_row1.addStretch()
        right_layout.addLayout(var_row1)

        # Variable buttons — row 2: non-padded variants + Korean weekday
        var_row2 = QHBoxLayout()
        for var in ["{H}", "{m}", "{s}", "{YY}", "{M}", "{D}", "{KW}"]:
            btn = QPushButton(var)
            btn.setFixedWidth(62)
            btn.clicked.connect(lambda _checked, v=var: self._editor.insert_variable(v))
            var_row2.addWidget(btn)
        var_row2.addStretch()
        right_layout.addLayout(var_row2)

        right_layout.addWidget(QLabel("템플릿 텍스트:"))
        self._editor = _TemplateEditor()
        self._editor.setMinimumHeight(80)
        self._editor.template_changed.connect(self._on_template_changed)
        right_layout.addWidget(self._editor)

        # Position / size (height is auto-fit; not user-editable)
        pos_group = QGroupBox("위치 / 크기")
        pos_layout = QHBoxLayout(pos_group)
        self._x_spin = QSpinBox()
        self._y_spin = QSpinBox()
        for spin, label in [
            (self._x_spin, "X"),
            (self._y_spin, "Y"),
        ]:
            spin.setRange(0, 9999)
            spin.setPrefix(f"{label}: ")
            spin.valueChanged.connect(self._on_geometry_changed)
            pos_layout.addWidget(spin)
        right_layout.addWidget(pos_group)

        # Font
        font_group = QGroupBox("폰트")
        font_layout = QHBoxLayout(font_group)
        self._font_combo = QFontComboBox()
        self._size_spin = QSpinBox()
        self._size_spin.setRange(6, 200)
        self._size_spin.setPrefix("크기: ")
        self._font_combo.currentFontChanged.connect(self._on_font_changed)
        self._size_spin.valueChanged.connect(self._on_font_changed)
        font_layout.addWidget(self._font_combo)
        font_layout.addWidget(self._size_spin)
        right_layout.addWidget(font_group)

        right_layout.addStretch()
        splitter.addWidget(right)
        splitter.setSizes([180, 480])
        main_layout.addWidget(splitter)

        # ── Bottom: window settings ─────────────────────────────────────────
        win_group = QGroupBox("창 설정")
        win_layout = QHBoxLayout(win_group)

        self._bg_btn = QPushButton("배경색")
        self._tc_btn = QPushButton("타이틀바 색상")
        self._aot_check = QCheckBox("항상 위")

        self._bg_btn.clicked.connect(self._pick_background_color)
        self._tc_btn.clicked.connect(self._pick_titlebar_color)
        self._aot_check.toggled.connect(self._on_always_on_top_changed)

        self._updating = True
        self._aot_check.setChecked(self._config.window.get("always_on_top", False))
        self._updating = False

        win_layout.addWidget(self._bg_btn)
        win_layout.addWidget(self._tc_btn)
        win_layout.addWidget(self._aot_check)
        win_layout.addStretch()
        main_layout.addWidget(win_group)

        self.resize(700, 520)

    # ── Textbox list management ─────────────────────────────────────────────

    def _load_textbox_list(self) -> None:
        self._list.blockSignals(True)
        self._list.clear()
        for tb_cfg in self._config.textboxes:
            item = QListWidgetItem(tb_cfg.get("template_text", "(빈)"))
            item.setData(Qt.ItemDataRole.UserRole, tb_cfg["id"])
            self._list.addItem(item)
        self._list.blockSignals(False)
        if self._list.count() > 0:
            self._list.setCurrentRow(0)

    def _on_selection_changed(self, current, _previous) -> None:
        if current is None:
            self._selected_id = None
            return
        self._selected_id = current.data(Qt.ItemDataRole.UserRole)
        self._load_selected()

    def _load_selected(self) -> None:
        if not self._selected_id:
            return
        cfg = next(
            (t for t in self._config.textboxes if t.get("id") == self._selected_id), None
        )
        if not cfg:
            return
        self._updating = True
        try:
            self._editor.load(cfg.get("template_text", ""), cfg.get("format_runs", []))
            self._x_spin.setValue(cfg.get("x", 0))
            self._y_spin.setValue(cfg.get("y", 0))
            self._font_combo.setCurrentFont(QFont(cfg.get("base_font_family", "Segoe UI")))
            self._size_spin.setValue(cfg.get("base_font_size", 24))
        finally:
            self._updating = False

    def _add_textbox(self) -> None:
        new_cfg = _make_default_textbox()
        new_cfg["y"] = max(10, len(self._config.textboxes) * 90 + 10)
        self._clock.add_textbox(new_cfg)
        item = QListWidgetItem(new_cfg["template_text"])
        item.setData(Qt.ItemDataRole.UserRole, new_cfg["id"])
        self._list.addItem(item)
        self._list.setCurrentItem(item)
        self._config.save()

    def _delete_textbox(self) -> None:
        if not self._selected_id or self._list.count() <= 1:
            return
        self._clock.remove_textbox(self._selected_id)
        row = self._list.currentRow()
        self._list.takeItem(row)
        self._config.save()

    # ── Editor callbacks ────────────────────────────────────────────────────

    def _on_template_changed(self, template_text: str, format_runs: object) -> None:
        if self._updating or not self._selected_id:
            return
        runs = list(format_runs) if format_runs else []
        self._clock.update_textbox(
            self._selected_id,
            {"template_text": template_text, "format_runs": runs},
        )
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == self._selected_id:
                item.setText(template_text or "(빈)")
                break
        self._schedule_save()

    def _on_geometry_changed(self) -> None:
        if self._updating or not self._selected_id:
            return
        self._clock.update_textbox(
            self._selected_id,
            {
                "x": self._x_spin.value(),
                "y": self._y_spin.value(),
            },
        )
        self._schedule_save()

    def _on_font_changed(self) -> None:
        if self._updating or not self._selected_id:
            return
        self._clock.update_textbox(
            self._selected_id,
            {
                "base_font_family": self._font_combo.currentFont().family(),
                "base_font_size": self._size_spin.value(),
            },
        )
        self._schedule_save()

    def _pick_text_color(self) -> None:
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self._editor.apply_formatting(color=color.name())

    # ── Window settings ─────────────────────────────────────────────────────

    def _pick_background_color(self) -> None:
        current = self._config.window.get("background_color", "#1e1e1e")
        color = QColorDialog.getColor(QColor(current), parent=self)
        if color.isValid():
            self._clock.set_background_color(color.name())
            self._config.save()

    def _pick_titlebar_color(self) -> None:
        current = self._config.window.get("titlebar_color", "#2b2b2b")
        color = QColorDialog.getColor(QColor(current), parent=self)
        if color.isValid():
            self._clock.set_titlebar_color(color.name())
            self._config.save()

    def _on_always_on_top_changed(self, checked: bool) -> None:
        if self._updating:
            return
        self._clock.set_always_on_top(checked)
        self._config.save()

    def _schedule_save(self) -> None:
        self._save_timer.start()
