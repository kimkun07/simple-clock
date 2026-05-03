import json
import os
from unittest.mock import patch

import pytest

from src.config import ConfigStore, _defaults, _make_default_textbox


def _patched_store(tmp_path):
    """Context manager that patches CONFIG_DIR and CONFIG_PATH to tmp_path."""
    config_path = str(tmp_path / "config.json")
    return (
        patch("src.config.CONFIG_DIR", str(tmp_path)),
        patch("src.config.CONFIG_PATH", config_path),
    )


def test_defaults_when_file_missing(tmp_path):
    p1, p2 = _patched_store(tmp_path)
    with p1, p2:
        store = ConfigStore.load()
    assert store.window["background_color"] == "#1e1e1e"
    assert store.window["always_on_top"] is False
    assert len(store.textboxes) == 1
    assert store.textboxes[0]["template_text"] == "{HH}:{mm}:{ss}"


def test_round_trip(tmp_path):
    config_path = str(tmp_path / "config.json")
    p1, p2 = _patched_store(tmp_path)
    with p1, p2:
        store = ConfigStore.load()
        store.window["background_color"] = "#ff0000"
        store.window["titlebar_color"] = "#aabbcc"
        store.save()
        store2 = ConfigStore.load()
    assert store2.window["background_color"] == "#ff0000"
    assert store2.window["titlebar_color"] == "#aabbcc"


def test_round_trip_textboxes(tmp_path):
    p1, p2 = _patched_store(tmp_path)
    with p1, p2:
        store = ConfigStore.load()
        store.textboxes[0]["template_text"] = "{YYYY}-{MM}-{DD}"
        store.save()
        store2 = ConfigStore.load()
    assert store2.textboxes[0]["template_text"] == "{YYYY}-{MM}-{DD}"


def test_corrupt_recovery(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("this is not valid json {{{{", encoding="utf-8")
    p1, p2 = _patched_store(tmp_path)
    with p1, p2:
        store = ConfigStore.load()
    assert store.window["background_color"] == "#1e1e1e"
    broken_files = [f for f in os.listdir(tmp_path) if f.startswith("config.broken")]
    assert len(broken_files) == 1


def test_corrupt_recovery_returns_defaults(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{bad json", encoding="utf-8")
    p1, p2 = _patched_store(tmp_path)
    with p1, p2:
        store = ConfigStore.load()
    defaults = _defaults()
    assert store.window["always_on_top"] == defaults["window"]["always_on_top"]
    assert len(store.textboxes) == 1


def test_atomic_save_creates_file(tmp_path):
    p1, p2 = _patched_store(tmp_path)
    with p1, p2:
        store = ConfigStore.load()
        store.save()
    assert (tmp_path / "config.json").exists()
    assert not (tmp_path / "config.json.tmp").exists()


def test_make_default_textbox_has_required_keys():
    tb = _make_default_textbox()
    for key in ("id", "x", "y", "width", "height", "template_text", "format_runs",
                "base_font_family", "base_font_size"):
        assert key in tb
