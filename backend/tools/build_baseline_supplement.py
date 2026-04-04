#!/usr/bin/env python3
"""
Build supplemental ground-truth baseline files from matched MoHA OCR reports.

Usage:
    PYTHONPATH=backend python backend/tools/build_baseline_supplement.py --years 2078 2079
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

from app.calendar.bikram_sambat import bs_to_gregorian

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
REPORTS_DIR = DATA_DIR / "ingest_reports"
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"
OVERRIDES_PATH = ROOT / "backend" / "app" / "calendar" / "ground_truth_overrides.json"

MONTH_VARIANTS = {
    "वैशाख": 1,
    "बैशाख": 1,
    "वेशाख": 1,
    "जेठ": 2,
    "असार": 3,
    "आषाढ": 3,
    "साउन": 4,
    "श्रावण": 4,
    "सावन": 4,
    "भदौ": 5,
    "भाद्र": 5,
    "असोज": 6,
    "आश्विन": 6,
    "अशोज": 6,
    "कात्तिक": 7,
    "कार्तिक": 7,
    "कातिक": 7,
    "मङ्सिर": 8,
    "मंसिर": 8,
    "पुस": 9,
    "पौष": 9,
    "माघ": 10,
    "फागुन": 11,
    "फाल्गुन": 11,
    "चैत": 12,
    "चैत्र": 12,
}

NEPALI_DIGIT_MAP = str.maketrans("०१२३४५६७८९", "0123456789")


@dataclass
class BaselineRecord:
    bs_year: int
    festival_id: str
    festival_name_raw: str
    bs_month_raw: str
    bs_month: int
    bs_day_raw: str
    bs_day: int
    gregorian_date: str
    source_file: str
    source_line: str
    source_citation: str
    extraction_confidence: float
    extraction_confidence_label: str
    status: str
    notes: str
    override_match: Optional[bool] = None
    override_date: Optional[dict] = None


def _confidence_label(score: float) -> str:
    if score >= 0.9:
        return "high"
    if score >= 0.75:
        return "medium"
    return "low"


def _calc_entry_confidence(
    festival_id: str, month_ok: bool, day_ok: bool, duplicate_count: int, unique_dates: int
) -> float:
    score = 0.0
    if festival_id:
        score += 0.45
    if month_ok:
        score += 0.2
    if day_ok:
        score += 0.2
    if duplicate_count == 1:
        score += 0.15
    elif unique_dates == 1:
        score += 0.08
    else:
        score -= 0.1
    return max(0.0, min(1.0, round(score, 2)))


def _to_int_day(raw: str) -> Optional[int]:
    try:
        return int((raw or "").translate(NEPALI_DIGIT_MAP))
    except ValueError:
        return None


def _load_overrides() -> dict:
    if not OVERRIDES_PATH.exists():
        return {}
    return json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))


def _read_matched_rows(year: int) -> list[dict[str, str]]:
    csv_path = REPORTS_DIR / f"holidays_{year}_matched.csv"
    if not csv_path.exists():
        return []
    with csv_path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_payload(years: list[int]) -> dict:
    overrides = _load_overrides()
    raw_rows: list[tuple[int, dict[str, str]]] = []
    for year in years:
        for row in _read_matched_rows(year):
            raw_rows.append((year, row))

    grouped: dict[tuple[int, str], list[tuple[int, dict[str, str]]]] = defaultdict(list)
    for bs_year, row in raw_rows:
        festival_id = (row.get("match_id") or "").strip()
        if festival_id:
            grouped[(bs_year, festival_id)].append((bs_year, row))

    records: list[BaselineRecord] = []
    for (bs_year, festival_id), items in grouped.items():
        converted_dates: list[str] = []
        parsed_items: list[tuple[dict[str, str], Optional[int], Optional[int], Optional[date], Optional[str]]] = []
        for _, row in items:
            month_raw = (row.get("month_raw") or "").strip()
            month_num = MONTH_VARIANTS.get(month_raw)
            day_raw = (row.get("day_raw") or "").strip()
            day_num = _to_int_day(day_raw)
            g_date = None
            err = None
            if month_num and day_num:
                try:
                    g_date = bs_to_gregorian(bs_year, month_num, day_num)
                    converted_dates.append(g_date.isoformat())
                except Exception as exc:  # noqa: BLE001
                    err = str(exc)
            parsed_items.append((row, month_num, day_num, g_date, err))

        unique_dates = sorted(set(converted_dates))
        status_for_group = "usable" if len(unique_dates) == 1 else "ambiguous"
        duplicate_count = len(items)

        for row, month_num, day_num, g_date, err in parsed_items:
            month_ok = month_num is not None
            day_ok = day_num is not None
            score = _calc_entry_confidence(
                festival_id, month_ok, day_ok, duplicate_count, len(unique_dates)
            )

            if g_date is None:
                status = "invalid"
                notes = err or "Could not convert BS->Gregorian"
                gregorian = ""
            else:
                status = status_for_group
                notes = (
                    "Ambiguous official date mapping in OCR rows" if status == "ambiguous" else "OK"
                )
                gregorian = g_date.isoformat()

            override_date = None
            override_match = None
            if g_date is not None:
                detail = overrides.get(str(g_date.year), {}).get(festival_id)
                if detail:
                    override_date = detail
                    if isinstance(detail, dict):
                        override_match = detail.get("start") == gregorian
                    elif isinstance(detail, str):
                        override_match = detail == gregorian

            records.append(
                BaselineRecord(
                    bs_year=bs_year,
                    festival_id=festival_id,
                    festival_name_raw=(row.get("name_raw") or "").strip(),
                    bs_month_raw=(row.get("month_raw") or "").strip(),
                    bs_month=month_num or 0,
                    bs_day_raw=(row.get("day_raw") or "").strip(),
                    bs_day=day_num or 0,
                    gregorian_date=gregorian,
                    source_file=f"holidays_{bs_year}_matched.csv",
                    source_line=(row.get("line") or "").strip(),
                    source_citation=f"MoHA Public Holidays {bs_year} BS (OCR matched)",
                    extraction_confidence=score,
                    extraction_confidence_label=_confidence_label(score),
                    status=status,
                    notes=notes,
                    override_match=override_match,
                    override_date=override_date,
                )
            )

    usable = [record for record in records if record.status == "usable"]
    ambiguous = [record for record in records if record.status == "ambiguous"]
    invalid = [record for record in records if record.status == "invalid"]

    return {
        "_meta": {
            "name": "Project Parva Supplemental Ground Truth Baseline",
            "bs_years": years,
            "generated_from": [f"data/ingest_reports/holidays_{year}_matched.csv" for year in years],
            "total_records": len(records),
            "usable_records": len(usable),
            "ambiguous_records": len(ambiguous),
            "invalid_records": len(invalid),
        },
        "records": [record.__dict__ for record in records],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int, required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    years = sorted(set(args.years))
    payload = build_payload(years)
    output = (
        Path(args.output)
        if args.output
        else GROUND_TRUTH_DIR / f"baseline_{years[0]}_{years[-1]}.json"
    )
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
