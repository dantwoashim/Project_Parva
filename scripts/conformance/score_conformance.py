#!/usr/bin/env python3
"""Score a Nepali Time Reliability conformance CSV."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path

LEVELS = ("bronze", "silver", "gold", "platinum")


@dataclass(frozen=True)
class ConformanceResult:
    level: str
    score: int
    max_score: int
    passed_checks: list[str]
    missing_checks: list[str]

    @property
    def score_percent(self) -> float:
        return round((self.score / self.max_score) * 100.0, 2) if self.max_score else 0.0


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def score_rows(rows: list[dict[str, str]]) -> dict[str, object]:
    check_names = {
        "bs_ad_conversion": any(row.get("workflow_type") == "bs_ad_conversion" for row in rows),
        "invalid_date_detection": any(row.get("expected_behavior") == "invalid_date" for row in rows),
        "supported_range_disclosure": any(row.get("supported_range") for row in rows),
        "holidays": any(row.get("workflow_type") == "holiday" for row in rows),
        "fiscal_years": any(row.get("workflow_type") == "fiscal_year" for row in rows),
        "working_days": any(row.get("workflow_type") == "working_day" for row in rows),
        "institution_profiles": any(row.get("institution_profile") for row in rows),
        "source_metadata": any(row.get("source_tier") for row in rows),
        "confidence_metadata": any(row.get("confidence") for row in rows),
        "review_required_behavior": any(str(row.get("review_required")).lower() == "true" for row in rows),
        "future_bs_boundary": any(row.get("workflow_type") == "future_bs_boundary" for row in rows),
        "panchanga": any(row.get("workflow_type") == "panchanga" for row in rows),
        "location_sensitive": any(row.get("location_sensitive") for row in rows),
        "benchmark_threshold": any(row.get("benchmark_score_percent") for row in rows),
        "evidence_packet_support": any(row.get("evidence_packet_id") for row in rows),
    }
    groups = {
        "bronze": ["bs_ad_conversion", "invalid_date_detection", "supported_range_disclosure"],
        "silver": ["holidays", "fiscal_years", "working_days", "institution_profiles"],
        "gold": ["source_metadata", "confidence_metadata", "review_required_behavior", "future_bs_boundary"],
        "platinum": ["panchanga", "location_sensitive", "benchmark_threshold", "evidence_packet_support"],
    }
    reports: dict[str, ConformanceResult] = {}
    cumulative: list[str] = []
    for level in LEVELS:
        cumulative.extend(groups[level])
        passed = [name for name in cumulative if check_names[name]]
        missing = [name for name in cumulative if not check_names[name]]
        reports[level] = ConformanceResult(level, len(passed), len(cumulative), passed, missing)

    achieved = "none"
    for level in LEVELS:
        if not reports[level].missing_checks:
            achieved = level
    return {
        "claim_boundary": "technical_conformance_report_not_certification",
        "not_authority": True,
        "rows": len(rows),
        "achieved_level": achieved,
        "levels": {
            level: {
                "score": result.score,
                "max_score": result.max_score,
                "score_percent": result.score_percent,
                "passed_checks": result.passed_checks,
                "missing_checks": result.missing_checks,
            }
            for level, result in reports.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    print(json.dumps(score_rows(_load_rows(Path(args.input))), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

