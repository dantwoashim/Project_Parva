#!/usr/bin/env python3
"""
Build/merge authoritative overrides from sources.json into ground_truth_overrides.json.

This is a helper to scale the gold-set over time without manual edits.
"""

import json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent / "app" / "calendar"
SOURCES_PATH = ROOT / "sources.json"
OVERRIDES_PATH = ROOT / "ground_truth_overrides.json"

# Map source keys to festival IDs
SOURCE_KEY_TO_FESTIVAL = {
    "makara_sankranti": "maghe-sankranti",
    "bs_new_year_2083": "bs-new-year",
    "shivaratri": "shivaratri",
    "holi": "holi",
    "buddha_jayanti": "buddha-jayanti",
    "teej": "teej",
    "indra_jatra": "indra-jatra",
    "dashain_ghatasthapana": "dashain",
    "dashain_vijaya_dashami": "vijaya-dashami",
    "tihar_kaag": "tihar",
    "tihar_bhai_tika": "bhai-tika",
}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def merge_sources_into_overrides():
    sources = load_json(SOURCES_PATH)
    overrides = load_json(OVERRIDES_PATH)
    if not overrides:
        overrides = {"_meta": {"description": "Authoritative overrides"}}

    ref = sources.get("reference_dates_2026", {})
    for key, entry in ref.items():
        fest = SOURCE_KEY_TO_FESTIVAL.get(key)
        if not fest:
            continue
        d = entry.get("date")
        if not d:
            continue
        y = str(date.fromisoformat(d).year)
        overrides.setdefault(y, {})
        overrides[y].setdefault(fest, {"start": d})

    save_json(OVERRIDES_PATH, overrides)
    print(f"✅ Updated overrides: {OVERRIDES_PATH}")


if __name__ == "__main__":
    merge_sources_into_overrides()
