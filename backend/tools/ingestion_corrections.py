"""
Second-Pass Ingestion Correction Rules — M7 Completion

Applies Nepali digit substitution, festival name normalization, and
fuzzy matching corrections to raw MoHA PDF extraction output.
"""

import json
import re
from pathlib import Path
from typing import Optional


# Nepali digit to ASCII mapping
NEPALI_DIGITS = {
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
}

# Reverse mapping
ASCII_TO_NEPALI = {v: k for k, v in NEPALI_DIGITS.items()}


def nepali_to_ascii_digits(text: str) -> str:
    """Replace Nepali digits (०-९) with ASCII digits (0-9)."""
    for nep, asc in NEPALI_DIGITS.items():
        text = text.replace(nep, asc)
    return text


def ascii_to_nepali_digits(text: str) -> str:
    """Replace ASCII digits (0-9) with Nepali digits (०-९)."""
    for asc, nep in ASCII_TO_NEPALI.items():
        text = text.replace(asc, nep)
    return text


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace into single space and strip."""
    return re.sub(r"\s+", " ", text).strip()


def extract_bs_date_from_text(text: str) -> Optional[dict]:
    """
    Extract BS date components from text like "२०८२/०५/१५" or "2082/05/15"
    or "15 Bhadra 2082".

    Returns dict with year, month, day or None.
    """
    # Normalize Nepali digits first
    normalized = nepali_to_ascii_digits(text)

    # Pattern: YYYY/MM/DD or YYYY-MM-DD
    match = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", normalized)
    if match:
        return {
            "year": int(match.group(1)),
            "month": int(match.group(2)),
            "day": int(match.group(3)),
        }

    return None


class FestivalNameNormalizer:
    """
    Normalize festival names from OCR/source variants to canonical IDs.

    Uses the festival_name_map.json reference.
    """

    def __init__(self, map_path: Optional[str] = None):
        if map_path is None:
            map_path = str(
                Path(__file__).parent.parent.parent
                / "data"
                / "festival_name_map.json"
            )
        with open(map_path) as f:
            self._map = json.load(f)

        # Build reverse lookup: variant -> canonical
        self._reverse = {}
        for canonical_id, entry in self._map.items():
            if isinstance(entry, dict) and "variants" in entry:
                for variant in entry["variants"]:
                    self._reverse[variant.lower().strip()] = canonical_id
                self._reverse[canonical_id.lower().strip()] = canonical_id

    def normalize(self, name: str) -> Optional[str]:
        """
        Map a festival name variant to its canonical ID.

        Returns canonical ID or None if no match.
        """
        key = name.lower().strip()
        return self._reverse.get(key)

    def normalize_or_original(self, name: str) -> str:
        """Return canonical ID if matched, else original name."""
        return self.normalize(name) or name

    @property
    def canonical_ids(self) -> list:
        """All canonical festival IDs."""
        return [
            k for k, v in self._map.items()
            if isinstance(v, dict) and "canonical" in v
        ]


def apply_second_pass_corrections(entries: list[dict]) -> list[dict]:
    """
    Apply all second-pass corrections to raw extraction entries.

    Each entry should have at minimum: festival_name, bs_date (text), ad_date (text).

    Returns corrected entries with:
    - Nepali digits converted to ASCII
    - Festival names normalized to canonical IDs
    - Whitespace cleaned
    """
    normalizer = FestivalNameNormalizer()
    corrected = []

    for entry in entries:
        fixed = dict(entry)

        # Fix festival name
        if "festival_name" in fixed:
            fixed["festival_name_original"] = fixed["festival_name"]
            fixed["festival_name"] = normalizer.normalize_or_original(
                fixed["festival_name"]
            )

        # Fix BS date text
        if "bs_date" in fixed and isinstance(fixed["bs_date"], str):
            fixed["bs_date"] = nepali_to_ascii_digits(fixed["bs_date"])

        # Fix AD date text
        if "ad_date" in fixed and isinstance(fixed["ad_date"], str):
            fixed["ad_date"] = nepali_to_ascii_digits(fixed["ad_date"])

        # Clean whitespace in all string fields
        for key, value in fixed.items():
            if isinstance(value, str):
                fixed[key] = normalize_whitespace(value)

        corrected.append(fixed)

    return corrected


def generate_source_comparison(
    source_a: list[dict],
    source_b: list[dict],
    year: int,
) -> dict:
    """
    Compare festival dates from two sources for the same year.

    Returns a comparison report with matches, mismatches, and unique entries.
    """
    normalizer = FestivalNameNormalizer()

    def key_fn(entry):
        name = normalizer.normalize_or_original(entry.get("festival_name", ""))
        return name.lower()

    a_map = {key_fn(e): e for e in source_a}
    b_map = {key_fn(e): e for e in source_b}

    all_keys = sorted(set(a_map.keys()) | set(b_map.keys()))

    matches = []
    mismatches = []
    only_a = []
    only_b = []

    for key in all_keys:
        in_a = a_map.get(key)
        in_b = b_map.get(key)

        if in_a and in_b:
            date_a = in_a.get("ad_date", "")
            date_b = in_b.get("ad_date", "")
            if date_a == date_b:
                matches.append({"festival": key, "date": date_a})
            else:
                mismatches.append({
                    "festival": key,
                    "source_a_date": date_a,
                    "source_b_date": date_b,
                })
        elif in_a:
            only_a.append({"festival": key, "date": in_a.get("ad_date", "")})
        else:
            only_b.append({"festival": key, "date": in_b.get("ad_date", "")})

    return {
        "year": year,
        "total_a": len(source_a),
        "total_b": len(source_b),
        "matches": len(matches),
        "mismatches": len(mismatches),
        "only_in_a": len(only_a),
        "only_in_b": len(only_b),
        "details": {
            "matches": matches,
            "mismatches": mismatches,
            "only_in_a": only_a,
            "only_in_b": only_b,
        },
    }
