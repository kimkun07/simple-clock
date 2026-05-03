import json
import os
import uuid
from datetime import datetime, timezone

CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "SimpleClock")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def _make_default_textbox() -> dict:
    return {
        "id": str(uuid.uuid4()),
        "x": 10,
        "y": 10,
        "width": 380,
        "height": 80,
        "template_text": "{HH}:{mm}:{ss}",
        "format_runs": [
            {"start": 0, "length": 8, "color": "#ffffff", "bold": False, "italic": False}
        ],
        "base_font_family": "Segoe UI",
        "base_font_size": 48,
    }


def _defaults() -> dict:
    return {
        "version": 1,
        "window": {
            "x": 100,
            "y": 100,
            "width": 420,
            "height": 160,
            "background_color": "#1e1e1e",
            "titlebar_color": "#2b2b2b",
            "always_on_top": False,
        },
        "textboxes": [_make_default_textbox()],
    }


class ConfigStore:
    def __init__(self, data: dict):
        self._data = data

    @classmethod
    def load(cls) -> "ConfigStore":
        os.makedirs(CONFIG_DIR, exist_ok=True)
        if not os.path.exists(CONFIG_PATH):
            return cls(_defaults())
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(data)
        except (json.JSONDecodeError, OSError, ValueError):
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            broken = os.path.join(CONFIG_DIR, f"config.broken.{ts}.json")
            try:
                os.replace(CONFIG_PATH, broken)
            except OSError:
                pass
            return cls(_defaults())

    def save(self) -> None:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        tmp = CONFIG_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, CONFIG_PATH)

    @property
    def window(self) -> dict:
        return self._data.setdefault("window", _defaults()["window"])

    @property
    def textboxes(self) -> list[dict]:
        return self._data.setdefault("textboxes", [])

    @textboxes.setter
    def textboxes(self, value: list[dict]) -> None:
        self._data["textboxes"] = value

    def to_dict(self) -> dict:
        return self._data
