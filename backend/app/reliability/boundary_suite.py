"""Boundary-suite regression helpers for calendar and lunar edge cases."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from app.calendar.lunar_calendar import detect_adhik_maas, lunar_month_boundaries, name_lunar_month
from app.calendar.sankranti import get_sankrantis_in_year
from app.calendar.tithi.tithi_udaya import detect_ksheepana, detect_vriddhi, get_udaya_tithi

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"
TITHI_FIXTURE = FIXTURES_DIR / "tithi_boundaries_30.json"
SANKRANTI_FIXTURE = FIXTURES_DIR / "sankranti_24.json"
ADHIK_FIXTURE = FIXTURES_DIR / "adhik_maas_reference.json"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {}


def _evaluate_tithi_boundaries() -> dict[str, Any]:
    data = _read_json(TITHI_FIXTURE)
    samples = data.get("samples", []) if isinstance(data.get("samples"), list) else []
    mismatches: list[dict[str, Any]] = []
    radar = Counter()

    for row in samples:
        target_date = date.fromisoformat(row["date"])
        actual = get_udaya_tithi(target_date)
        expected_sunrise = datetime.fromisoformat(row["sunrise_utc"])
        sunrise_delta_seconds = abs((actual["sunrise"] - expected_sunrise).total_seconds())
        expected_delta_hours = float(row.get("delta_hours") or 0.0)

        if expected_delta_hours <= 0.5:
            radar["high_disagreement_risk"] += 1
        elif expected_delta_hours <= 1.5:
            radar["one_day_sensitive"] += 1
        else:
            radar["stable"] += 1

        failed = (
            actual["tithi"] != row["tithi"]
            or actual["paksha"] != row["paksha"]
            or detect_vriddhi(target_date) != row["vriddhi"]
            or detect_ksheepana(target_date) != row["ksheepana"]
            or sunrise_delta_seconds > 60
        )
        if failed:
            mismatches.append(
                {
                    "date": row["date"],
                    "expected_tithi": row["tithi"],
                    "actual_tithi": actual["tithi"],
                    "expected_paksha": row["paksha"],
                    "actual_paksha": actual["paksha"],
                    "expected_vriddhi": row["vriddhi"],
                    "actual_vriddhi": detect_vriddhi(target_date),
                    "expected_ksheepana": row["ksheepana"],
                    "actual_ksheepana": detect_ksheepana(target_date),
                    "sunrise_delta_seconds": sunrise_delta_seconds,
                }
            )

    total = len(samples)
    return {
        "suite_id": "tithi_boundaries_30",
        "category": "sunrise_flips",
        "fixture_path": str(TITHI_FIXTURE.relative_to(PROJECT_ROOT)),
        "samples": total,
        "passed": total - len(mismatches),
        "failed": len(mismatches),
        "pass_rate": round((total - len(mismatches)) / total, 4) if total else 0.0,
        "boundary_radar_counts": dict(radar),
        "mismatches": mismatches[:5],
    }


def _evaluate_sankranti_boundaries() -> dict[str, Any]:
    data = _read_json(SANKRANTI_FIXTURE)
    rows = data.get("sankrantis", []) if isinstance(data.get("sankrantis"), list) else []
    by_year: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_year.setdefault(int(row["year"]), []).append(row)

    mismatches: list[dict[str, Any]] = []
    for year, expected_rows in by_year.items():
        actual_rows = get_sankrantis_in_year(year)
        if len(actual_rows) != len(expected_rows):
            mismatches.append(
                {
                    "year": year,
                    "reason": "count_mismatch",
                    "expected_count": len(expected_rows),
                    "actual_count": len(actual_rows),
                }
            )
            continue
        for expected, actual in zip(expected_rows, actual_rows):
            expected_dt = datetime.fromisoformat(expected["datetime_utc"])
            delta_seconds = abs((actual["datetime_utc"] - expected_dt).total_seconds())
            if (
                actual["rashi_index"] != expected["rashi_index"]
                or actual["rashi_name"] != expected["rashi_name"]
                or actual["date"].isoformat() != expected["date"]
                or delta_seconds > 120
            ):
                mismatches.append(
                    {
                        "year": year,
                        "rashi_name": expected["rashi_name"],
                        "expected_date": expected["date"],
                        "actual_date": actual["date"].isoformat(),
                        "delta_seconds": delta_seconds,
                    }
                )

    total = len(rows)
    failed = len(mismatches)
    passed = max(total - failed, 0)
    return {
        "suite_id": "sankranti_24",
        "category": "sankranti_boundaries",
        "fixture_path": str(SANKRANTI_FIXTURE.relative_to(PROJECT_ROOT)),
        "samples": total,
        "years": sorted(by_year),
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "mismatches": mismatches[:5],
    }


def _adhik_month_names(gregorian_year: int) -> list[str]:
    names: list[str] = []
    for start, end in lunar_month_boundaries(gregorian_year):
        if detect_adhik_maas(start, end):
            names.append(f"Adhik {name_lunar_month(start, end)}")
    return names


def _evaluate_adhik_reference() -> dict[str, Any]:
    data = _read_json(ADHIK_FIXTURE)
    rows = data.get("years", []) if isinstance(data.get("years"), list) else []
    mismatches: list[dict[str, Any]] = []

    for row in rows:
        gregorian_year = int(row["gregorian_year"])
        actual_names = _adhik_month_names(gregorian_year)
        expected_names = list(row.get("adhik_months") or [])
        actual_has_adhik = bool(actual_names)
        expected_has_adhik = bool(row.get("has_adhik"))
        if actual_has_adhik != expected_has_adhik or actual_names != expected_names:
            mismatches.append(
                {
                    "bs_year": row["bs_year"],
                    "gregorian_year": gregorian_year,
                    "expected_has_adhik": expected_has_adhik,
                    "actual_has_adhik": actual_has_adhik,
                    "expected_adhik_months": expected_names,
                    "actual_adhik_months": actual_names,
                }
            )

    total = len(rows)
    failed = len(mismatches)
    passed = max(total - failed, 0)
    return {
        "suite_id": "adhik_maas_reference",
        "category": "lunar_month_transitions",
        "fixture_path": str(ADHIK_FIXTURE.relative_to(PROJECT_ROOT)),
        "samples": total,
        "range_bs": (data.get("metadata") or {}).get("range_bs"),
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "mismatches": mismatches[:5],
    }


def get_boundary_suite() -> dict[str, Any]:
    suites = [
        _evaluate_tithi_boundaries(),
        _evaluate_sankranti_boundaries(),
        _evaluate_adhik_reference(),
    ]
    total_samples = sum(int(item.get("samples", 0)) for item in suites)
    total_failed = sum(int(item.get("failed", 0)) for item in suites)
    total_passed = sum(int(item.get("passed", 0)) for item in suites)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "suite_count": len(suites),
        "total_samples": total_samples,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "pass_rate": round(total_passed / total_samples, 4) if total_samples else 0.0,
        "suites": suites,
    }


__all__ = ["get_boundary_suite"]
