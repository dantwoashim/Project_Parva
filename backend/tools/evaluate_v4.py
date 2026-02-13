#!/usr/bin/env python3
"""Configurable evaluation harness with by-festival and by-rule scorecards."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from app.calendar.calculator_v2 import calculate_festival_v2, get_festival_rules_v3
try:
    from evaluate import TEST_CASES_2026, load_moha_matched_tests
except ModuleNotFoundError:  # pragma: no cover - import path fallback
    from backend.tools.evaluate import TEST_CASES_2026, load_moha_matched_tests

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class EvalRow:
    festival_id: str
    year: int
    expected_date: str
    calculated_date: str | None
    passed: bool
    variance_days: int | None
    source: str
    notes: str
    rule_type: str
    probable_cause: str


def variance_days(expected: str, calculated: str | None) -> int | None:
    if not calculated:
        return None
    e = datetime.strptime(expected, "%Y-%m-%d").date()
    c = datetime.strptime(calculated, "%Y-%m-%d").date()
    return abs((c - e).days)


def classify_cause(passed: bool, error: str | None, delta: int | None) -> str:
    if passed:
        return "match"
    if error:
        return "calculation_error"
    if delta is None:
        return "missing_result"
    if delta == 1:
        return "boundary_shift"
    if delta > 1:
        return "rule_or_source_mismatch"
    return "unknown"


def get_rule_type(festival_id: str) -> str:
    rules = get_festival_rules_v3()
    rule = rules.get(festival_id)
    if rule is None:
        return "fallback"
    return rule.type


def load_cases(include_moha: bool) -> list[tuple[str, str, str, str]]:
    cases = list(TEST_CASES_2026)
    if include_moha:
        report_dir = PROJECT_ROOT / "data" / "ingest_reports"
        if report_dir.exists():
            cases.extend(load_moha_matched_tests(report_dir))
    return cases


def evaluate_case(festival_id: str, expected: str, source: str, notes: str, tolerance: int, use_overrides: bool) -> EvalRow:
    year = int(expected[:4])
    rule_type = get_rule_type(festival_id)
    try:
        result = calculate_festival_v2(festival_id, year, use_overrides=use_overrides)
        calc = result.start_date.isoformat() if result else None
        delta = variance_days(expected, calc)
        passed = delta is not None and delta <= tolerance
        cause = classify_cause(passed, None, delta)
        return EvalRow(
            festival_id=festival_id,
            year=year,
            expected_date=expected,
            calculated_date=calc,
            passed=passed,
            variance_days=delta,
            source=source,
            notes=notes,
            rule_type=rule_type,
            probable_cause=cause,
        )
    except Exception as exc:
        return EvalRow(
            festival_id=festival_id,
            year=year,
            expected_date=expected,
            calculated_date=None,
            passed=False,
            variance_days=None,
            source=source,
            notes=notes,
            rule_type=rule_type,
            probable_cause=classify_cause(False, str(exc), None),
        )


def summarize(rows: Iterable[EvalRow]) -> dict:
    rows = list(rows)
    total = len(rows)
    passed = sum(1 for r in rows if r.passed)

    by_festival: dict[str, dict[str, float | int]] = defaultdict(lambda: {"total": 0, "passed": 0})
    by_rule: dict[str, dict[str, float | int]] = defaultdict(lambda: {"total": 0, "passed": 0})
    cause_counts: dict[str, int] = defaultdict(int)

    for row in rows:
        by_festival[row.festival_id]["total"] += 1
        by_rule[row.rule_type]["total"] += 1
        if row.passed:
            by_festival[row.festival_id]["passed"] += 1
            by_rule[row.rule_type]["passed"] += 1
        cause_counts[row.probable_cause] += 1

    for bucket in (by_festival, by_rule):
        for stats in bucket.values():
            total_i = int(stats["total"])
            stats["pass_rate"] = round((int(stats["passed"]) / total_i) * 100.0, 2) if total_i else 0.0

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round((passed / total) * 100.0, 2) if total else 0.0,
        "by_festival": dict(sorted(by_festival.items())),
        "by_rule": dict(sorted(by_rule.items())),
        "causes": dict(sorted(cause_counts.items())),
    }


def write_csv(rows: list[EvalRow], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()) if rows else [
            "festival_id", "year", "expected_date", "calculated_date", "passed",
            "variance_days", "source", "notes", "rule_type", "probable_cause"
        ])
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_json(rows: list[EvalRow], summary: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "summary": summary,
                "rows": [asdict(r) for r in rows],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def write_markdown(rows: list[EvalRow], summary: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Evaluation V4 Report",
        "",
        f"- Total: **{summary['total']}**",
        f"- Passed: **{summary['passed']}**",
        f"- Failed: **{summary['failed']}**",
        f"- Pass rate: **{summary['pass_rate']}%**",
        "",
        "## By Rule Type",
        "",
        "| Rule Type | Passed | Total | Pass Rate |",
        "|---|---:|---:|---:|",
    ]

    for rule, stats in summary["by_rule"].items():
        lines.append(f"| {rule} | {stats['passed']} | {stats['total']} | {stats['pass_rate']}% |")

    lines += [
        "",
        "## By Festival",
        "",
        "| Festival | Passed | Total | Pass Rate |",
        "|---|---:|---:|---:|",
    ]

    for festival, stats in summary["by_festival"].items():
        lines.append(f"| {festival} | {stats['passed']} | {stats['total']} | {stats['pass_rate']}% |")

    lines += [
        "",
        "## Failure Causes",
        "",
        "| Cause | Count |",
        "|---|---:|",
    ]

    for cause, count in summary["causes"].items():
        lines.append(f"| {cause} | {count} |")

    failures = [r for r in rows if not r.passed]
    if failures:
        lines += [
            "",
            "## Failures",
            "",
            "| Festival | Year | Expected | Calculated | Rule | Cause |",
            "|---|---:|---|---|---|---|",
        ]
        for row in failures:
            lines.append(
                f"| {row.festival_id} | {row.year} | {row.expected_date} | {row.calculated_date or 'N/A'} | {row.rule_type} | {row.probable_cause} |"
            )

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluation harness v4")
    parser.add_argument("--year-from", type=int, default=None, help="Filter cases with year >= this")
    parser.add_argument("--year-to", type=int, default=None, help="Filter cases with year <= this")
    parser.add_argument("--festival", action="append", default=[], help="Festival id filter (repeatable)")
    parser.add_argument("--variance", type=int, default=1, help="Allowed variance in days")
    parser.add_argument("--no-overrides", action="store_true", help="Disable official overrides")
    parser.add_argument("--no-moha", action="store_true", help="Disable OCR-expanded MoHA cases")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "reports" / "evaluation_v4"), help="Output directory")
    args = parser.parse_args()

    cases = load_cases(include_moha=not args.no_moha)

    if args.year_from is not None:
        cases = [c for c in cases if int(c[1][:4]) >= args.year_from]
    if args.year_to is not None:
        cases = [c for c in cases if int(c[1][:4]) <= args.year_to]
    if args.festival:
        wanted = set(args.festival)
        cases = [c for c in cases if c[0] in wanted]

    rows = [
        evaluate_case(fid, expected, source, notes, args.variance, use_overrides=not args.no_overrides)
        for fid, expected, source, notes in cases
    ]

    summary = summarize(rows)

    out_dir = Path(args.output_dir)
    write_csv(rows, out_dir / "evaluation_v4.csv")
    write_json(rows, summary, out_dir / "evaluation_v4.json")
    write_markdown(rows, summary, out_dir / "evaluation_v4.md")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
