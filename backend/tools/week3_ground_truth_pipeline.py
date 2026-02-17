#!/usr/bin/env python3
"""
Year 1 Week 3 Ground-Truth Pipeline
===================================

Builds:
1) baseline_2080_2082.json from MoHA OCR matched CSVs
2) discrepancies.json comparing V2 (no overrides) vs official entries
3) scorecard_2080_2082.{json,md} with by-festival and by-rule breakdown

Usage:
    PYTHONPATH=backend python3 backend/tools/week3_ground_truth_pipeline.py
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
REPORTS_DIR = DATA_DIR / "ingest_reports"
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"
GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)

OVERRIDES_PATH = ROOT / "backend" / "app" / "calendar" / "ground_truth_overrides.json"

TARGET_BS_YEARS = [2080, 2081, 2082]

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
    status: str  # usable | ambiguous | invalid
    notes: str
    override_match: Optional[bool] = None
    override_date: Optional[str] = None


def _confidence_label(score: float) -> str:
    if score >= 0.9:
        return "high"
    if score >= 0.75:
        return "medium"
    return "low"


def _calc_entry_confidence(
    festival_id: str, month_ok: bool, day_ok: bool, duplicate_count: int, unique_dates: int
) -> float:
    # deterministic heuristic to keep confidence explicit in baseline
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


def _load_overrides() -> Dict[str, Dict[str, str]]:
    if not OVERRIDES_PATH.exists():
        return {}
    data = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if k.isdigit() and isinstance(v, dict)}


def _read_matched_rows(year: int) -> List[Dict[str, str]]:
    csv_path = REPORTS_DIR / f"holidays_{year}_matched.csv"
    if not csv_path.exists():
        return []
    with csv_path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_int_day(raw: str) -> Optional[int]:
    try:
        return int((raw or "").translate(NEPALI_DIGIT_MAP))
    except ValueError:
        return None


def build_baseline() -> Dict[str, Any]:
    from app.calendar.bikram_sambat import bs_to_gregorian

    overrides = _load_overrides()
    raw_rows: List[Tuple[int, Dict[str, str]]] = []
    for year in TARGET_BS_YEARS:
        rows = _read_matched_rows(year)
        for row in rows:
            raw_rows.append((year, row))

    # group by (bs_year, festival_id) for ambiguity/confidence
    grouped: Dict[Tuple[int, str], List[Tuple[int, Dict[str, str]]]] = defaultdict(list)
    for bs_year, row in raw_rows:
        festival_id = (row.get("match_id") or "").strip()
        if not festival_id:
            continue
        grouped[(bs_year, festival_id)].append((bs_year, row))

    baseline_records: List[BaselineRecord] = []

    for (bs_year, festival_id), items in grouped.items():
        converted_dates: List[str] = []
        parsed_items: List[Tuple[Dict[str, str], Optional[int], Optional[int], Optional[date], Optional[str]]] = []
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
                except Exception as e:  # noqa: BLE001
                    err = str(e)
            parsed_items.append((row, month_num, day_num, g_date, err))

        unique_dates = sorted(set(converted_dates))
        duplicate_count = len(items)
        status_for_group = "usable" if len(unique_dates) == 1 else "ambiguous"

        for row, month_num, day_num, g_date, err in parsed_items:
            month_ok = month_num is not None
            day_ok = day_num is not None
            score = _calc_entry_confidence(
                festival_id=festival_id,
                month_ok=month_ok,
                day_ok=day_ok,
                duplicate_count=duplicate_count,
                unique_dates=len(unique_dates),
            )

            if g_date is None:
                status = "invalid"
                notes = err or "Could not convert BS->Gregorian"
                gregorian = ""
            else:
                status = status_for_group
                notes = "Ambiguous official date mapping in OCR rows" if status == "ambiguous" else "OK"
                gregorian = g_date.isoformat()

            override_date = None
            override_match = None
            if g_date is not None:
                g_year_key = str(g_date.year)
                override_year = overrides.get(g_year_key, {})
                if festival_id in override_year:
                    override_date = override_year[festival_id]
                    override_match = (override_date == gregorian)

            source_file = f"holidays_{bs_year}_matched.csv"
            source_citation = f"MoHA Public Holidays {bs_year} BS (OCR matched)"
            baseline_records.append(
                BaselineRecord(
                    bs_year=bs_year,
                    festival_id=festival_id,
                    festival_name_raw=(row.get("name_raw") or "").strip(),
                    bs_month_raw=(row.get("month_raw") or "").strip(),
                    bs_month=month_num or 0,
                    bs_day_raw=(row.get("day_raw") or "").strip(),
                    bs_day=day_num or 0,
                    gregorian_date=gregorian,
                    source_file=source_file,
                    source_line=(row.get("line") or "").strip(),
                    source_citation=source_citation,
                    extraction_confidence=score,
                    extraction_confidence_label=_confidence_label(score),
                    status=status,
                    notes=notes,
                    override_match=override_match,
                    override_date=override_date,
                )
            )

    records_json = [r.__dict__ for r in baseline_records]
    usable = [r for r in baseline_records if r.status == "usable"]
    ambiguous = [r for r in baseline_records if r.status == "ambiguous"]
    invalid = [r for r in baseline_records if r.status == "invalid"]

    payload = {
        "_meta": {
            "name": "Project Parva Week3 Ground Truth Baseline",
            "bs_years": TARGET_BS_YEARS,
            "generated_from": "data/ingest_reports/holidays_{year}_matched.csv",
            "total_records": len(records_json),
            "usable_records": len(usable),
            "ambiguous_records": len(ambiguous),
            "invalid_records": len(invalid),
        },
        "records": records_json,
    }
    out_path = GROUND_TRUTH_DIR / "baseline_2080_2082.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def _rule_group(festival_id: str) -> str:
    v3_path = ROOT / "backend" / "app" / "calendar" / "festival_rules_v3.json"
    if not v3_path.exists():
        return "unknown"
    v3 = json.loads(v3_path.read_text(encoding="utf-8")).get("festivals", {})
    rule = v3.get(festival_id)
    if not rule:
        return "legacy_fallback"
    return str(rule.get("type", "unknown"))


def build_discrepancy_and_scorecard(baseline: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    from app.calendar.calculator_v2 import calculate_festival_v2

    records = baseline.get("records", [])
    usable_records = [
        r for r in records
        if r.get("status") == "usable" and r.get("gregorian_date")
    ]

    discrepancies: List[Dict[str, Any]] = []
    by_festival: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"total": 0, "exact": 0, "off_by_1": 0, "failed": 0, "exact_with_overrides": 0}
    )
    by_rule: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"total": 0, "exact": 0, "off_by_1": 0, "failed": 0, "exact_with_overrides": 0}
    )
    by_year: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"total": 0, "exact": 0, "off_by_1": 0, "failed": 0, "exact_with_overrides": 0}
    )

    exact_with_overrides = 0

    for row in usable_records:
        festival_id = row["festival_id"]
        official = date.fromisoformat(row["gregorian_date"])
        year = official.year
        rule = _rule_group(festival_id)

        stats_targets = (by_festival[festival_id], by_rule[rule], by_year[str(row["bs_year"])])
        for t in stats_targets:
            t["total"] += 1

        calc_no = calculate_festival_v2(festival_id, year, use_overrides=False)
        calc_yes = calculate_festival_v2(festival_id, year, use_overrides=True)
        if calc_yes and calc_yes.start_date == official:
            exact_with_overrides += 1
            for t in stats_targets:
                t["exact_with_overrides"] += 1

        if calc_no is None:
            for t in stats_targets:
                t["failed"] += 1
            discrepancies.append(
                {
                    "festival_id": festival_id,
                    "bs_year": row["bs_year"],
                    "official_date": row["gregorian_date"],
                    "calculated_date_no_overrides": None,
                    "calculated_date_with_overrides": calc_yes.start_date.isoformat() if calc_yes else None,
                    "delta_days_no_overrides": None,
                    "probable_cause": "no_rule_or_calc_failure",
                    "source_citation": row["source_citation"],
                }
            )
            continue

        calculated = calc_no.start_date
        delta = (calculated - official).days
        abs_delta = abs(delta)

        if abs_delta == 0:
            for t in stats_targets:
                t["exact"] += 1
            continue
        if abs_delta == 1:
            for t in stats_targets:
                t["off_by_1"] += 1

        if calc_no.method == "fallback_v1":
            cause = "legacy_rule_fallback"
        elif abs_delta >= 25:
            cause = "adhik_maas_or_lunar_month_alignment"
        elif abs_delta >= 7:
            cause = "rule_definition_or_month_alignment"
        elif abs_delta == 1:
            cause = "tithi_boundary_or_timezone"
        else:
            cause = "minor_rule_alignment"

        discrepancies.append(
            {
                "festival_id": festival_id,
                "bs_year": row["bs_year"],
                "official_date": row["gregorian_date"],
                "calculated_date_no_overrides": calculated.isoformat(),
                "calculated_date_with_overrides": calc_yes.start_date.isoformat() if calc_yes else None,
                "delta_days_no_overrides": delta,
                "method_no_overrides": calc_no.method,
                "probable_cause": cause,
                "source_citation": row["source_citation"],
            }
        )

    discrepancy_payload = {
        "_meta": {
            "name": "Project Parva Week3 Discrepancy Register",
            "scope": "Usable MoHA matched entries (BS 2080-2082)",
            "comparison_mode": "V2 without overrides vs official baseline",
            "total_usable_entries": len(usable_records),
            "total_discrepancies": len(discrepancies),
        },
        "discrepancies": discrepancies,
    }
    (GROUND_TRUTH_DIR / "discrepancies.json").write_text(
        json.dumps(discrepancy_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    def _with_rates(stats: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        out: Dict[str, Dict[str, Any]] = {}
        for k, v in sorted(stats.items()):
            total = v["total"] or 1
            out[k] = {
                **v,
                "exact_rate": round(v["exact"] / total * 100, 2),
                "off_by_1_rate": round(v["off_by_1"] / total * 100, 2),
                "failed_rate": round(v["failed"] / total * 100, 2),
                "exact_with_overrides_rate": round(v["exact_with_overrides"] / total * 100, 2),
            }
        return out

    scorecard_payload = {
        "_meta": {
            "name": "Project Parva Week3 Accuracy Scorecard",
            "scope": "Usable MoHA matched entries (BS 2080-2082)",
            "mode": "V2 without overrides",
            "reference_mode": "V2 with overrides",
            "total_usable_entries": len(usable_records),
            "total_discrepancies": len(discrepancies),
            "exact_match_rate": round((len(usable_records) - len(discrepancies)) / (len(usable_records) or 1) * 100, 2),
            "exact_match_rate_with_overrides": round(exact_with_overrides / (len(usable_records) or 1) * 100, 2),
        },
        "by_festival": _with_rates(by_festival),
        "by_rule_group": _with_rates(by_rule),
        "by_bs_year": _with_rates(by_year),
    }
    (GROUND_TRUTH_DIR / "scorecard_2080_2082.json").write_text(
        json.dumps(scorecard_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return discrepancy_payload, scorecard_payload


def write_scorecard_markdown(scorecard: Dict[str, Any]) -> None:
    meta = scorecard["_meta"]
    lines = [
        "# Week3 Accuracy Scorecard (BS 2080-2082)",
        "",
        f"- Total usable entries: **{meta['total_usable_entries']}**",
        f"- Exact match rate (V2 without overrides): **{meta['exact_match_rate']}%**",
        f"- Exact match rate (V2 with overrides): **{meta['exact_match_rate_with_overrides']}%**",
        f"- Total discrepancies: **{meta['total_discrepancies']}**",
        "",
        "## By Rule Group",
        "",
        "| Rule Group | Total | Exact | Exact (Overrides) | Off by 1 | Failed | Exact Rate | Exact (Overrides) Rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group, stats in scorecard["by_rule_group"].items():
        lines.append(
            f"| {group} | {stats['total']} | {stats['exact']} | {stats['exact_with_overrides']} | {stats['off_by_1']} | {stats['failed']} | {stats['exact_rate']}% | {stats['exact_with_overrides_rate']}% |"
        )

    lines += [
        "",
        "## By BS Year",
        "",
        "| BS Year | Total | Exact | Exact (Overrides) | Off by 1 | Failed | Exact Rate | Exact (Overrides) Rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for bs_year, stats in scorecard["by_bs_year"].items():
        lines.append(
            f"| {bs_year} | {stats['total']} | {stats['exact']} | {stats['exact_with_overrides']} | {stats['off_by_1']} | {stats['failed']} | {stats['exact_rate']}% | {stats['exact_with_overrides_rate']}% |"
        )

    (GROUND_TRUTH_DIR / "scorecard_2080_2082.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    baseline = build_baseline()
    _, scorecard = build_discrepancy_and_scorecard(baseline)
    write_scorecard_markdown(scorecard)
    print("Generated:")
    print(f" - {GROUND_TRUTH_DIR / 'baseline_2080_2082.json'}")
    print(f" - {GROUND_TRUTH_DIR / 'discrepancies.json'}")
    print(f" - {GROUND_TRUTH_DIR / 'scorecard_2080_2082.json'}")
    print(f" - {GROUND_TRUTH_DIR / 'scorecard_2080_2082.md'}")


if __name__ == "__main__":
    main()
