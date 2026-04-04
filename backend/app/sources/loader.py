"""JSON-backed source loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .interface import SourceInterface
from .validation import validate_ground_truth_payload

DEFAULT_PRIORITY = [
    "ground_truth_overrides",
    "moha_official",
    "rashtriya_panchang",
    "secondary_digital_provider",
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
        ground_truth_dir = self.data_dir / "ground_truth"
        payloads = []
        for path in sorted(ground_truth_dir.glob("baseline_*.json")):
            payload = self._read_json(path, {})
            if isinstance(payload, dict):
                payloads.append(payload)

        if not payloads:
            return {}

        merged_records: list[dict[str, Any]] = []
        bs_years: list[int] = []
        total_records = 0
        usable_records = 0
        ambiguous_records = 0
        invalid_records = 0

        for payload in payloads:
            meta = payload.get("_meta", {})
            merged_records.extend(payload.get("records", []))
            for year in meta.get("bs_years", []):
                try:
                    bs_years.append(int(year))
                except (TypeError, ValueError):
                    continue
            total_records += int(meta.get("total_records", 0) or 0)
            usable_records += int(meta.get("usable_records", 0) or 0)
            ambiguous_records += int(meta.get("ambiguous_records", 0) or 0)
            invalid_records += int(meta.get("invalid_records", 0) or 0)

        merged_payload = {
            "_meta": {
                "name": "Project Parva MoHA Ground Truth Baseline",
                "source_files": [path.name for path in sorted(ground_truth_dir.glob("baseline_*.json"))],
                "bs_years": sorted(set(bs_years)),
                "total_records": total_records or len(merged_records),
                "usable_records": usable_records,
                "ambiguous_records": ambiguous_records,
                "invalid_records": invalid_records,
            },
            "records": merged_records,
        }
        merged_payload["_meta"]["validation"] = validate_ground_truth_payload(merged_payload)
        return merged_payload

    def load_festival_rules(self) -> dict[str, Any]:
        return self._read_json(self.calendar_dir / "festival_rules_v3.json", {"festivals": {}})

    def load_overrides(self) -> dict[str, Any]:
        return self._read_json(self.calendar_dir / "ground_truth_overrides.json", {})

    def get_source_priority(self) -> list[str]:
        return DEFAULT_PRIORITY.copy()


def get_source_loader() -> JsonSourceLoader:
    """Factory for default source loader."""
    return JsonSourceLoader()
