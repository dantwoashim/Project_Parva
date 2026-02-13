"""JSON-backed source loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .interface import SourceInterface


DEFAULT_PRIORITY = [
    "ground_truth_overrides",
    "moha_official",
    "rashtriya_panchang",
    "computed_ephemeris",
    "ocr_extracted",
]


class JsonSourceLoader(SourceInterface):
    """Loads source artifacts from the repository data folders."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[3]
        self.calendar_dir = self.root / "backend" / "app" / "calendar"
        self.data_dir = self.root / "data"

    def _read_json(self, path: Path, fallback: Any) -> Any:
        if not path.exists():
            return fallback
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def load_ground_truth(self) -> dict[str, Any]:
        return self._read_json(
            self.data_dir / "ground_truth" / "baseline_2080_2082.json",
            {},
        )

    def load_festival_rules(self) -> dict[str, Any]:
        return self._read_json(self.calendar_dir / "festival_rules_v3.json", {"festivals": {}})

    def load_overrides(self) -> dict[str, Any]:
        return self._read_json(self.calendar_dir / "ground_truth_overrides.json", {})

    def get_source_priority(self) -> list[str]:
        return DEFAULT_PRIORITY.copy()


def get_source_loader() -> JsonSourceLoader:
    """Factory for default source loader."""
    return JsonSourceLoader()
