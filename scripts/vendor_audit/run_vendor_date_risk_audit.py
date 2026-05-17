#!/usr/bin/env python3
"""Run a public-safe BS Date Risk Audit over a vendor CSV."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.calendar.bikram_sambat import bs_to_gregorian  # noqa: E402
from app.calendar.provenance import get_bs_year_provenance  # noqa: E402

REQUIRED_COLUMNS = {"bs_date", "workflow_type", "expected_behavior"}
REVIEW_SENSITIVE_WORKFLOWS = {"payroll", "loan", "bank", "tax", "legal", "repayment"}


@dataclass(frozen=True)
class AuditRow:
    row_number: int
    bs_date: str
    workflow_type: str
    expected_behavior: str
    actual_ad_date: str | None
    holiday_assumption: str | None
    fiscal_assumption: str | None


def _parse_bs_date(value: str) -> tuple[int, int, int]:
    year_raw, month_raw, day_raw = value.split("-", 2)
    return int(year_raw), int(month_raw), int(day_raw)


def _load_rows(path: Path) -> list[AuditRow]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Input CSV missing required columns: {', '.join(sorted(missing))}")
        rows = []
        for index, row in enumerate(reader, start=2):
            rows.append(
                AuditRow(
                    row_number=index,
                    bs_date=(row.get("bs_date") or "").strip(),
                    workflow_type=(row.get("workflow_type") or "").strip(),
                    expected_behavior=(row.get("expected_behavior") or "").strip(),
                    actual_ad_date=(row.get("actual_ad_date") or "").strip() or None,
                    holiday_assumption=(row.get("holiday_assumption") or "").strip() or None,
                    fiscal_assumption=(row.get("fiscal_assumption") or "").strip() or None,
                )
            )
    return rows


def _row_issue(row: AuditRow, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "row_number": row.row_number,
        "bs_date": row.bs_date,
        "workflow_type": row.workflow_type,
        "expected_behavior": row.expected_behavior,
        "reason": reason,
        **extra,
    }


def audit_rows(rows: list[AuditRow]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "summary": {
            "rows": len(rows),
            "claim_boundary": "technical_conformance_report_not_certification",
            "not_authority": True,
        },
        "invalid_dates": [],
        "holiday_mismatches": [],
        "working_day_mismatches": [],
        "fiscal_cutoff_errors": [],
        "unsupported_future_assumptions": [],
        "source_conflicts": [],
        "review_required_cases": [],
        "recommendations": [],
    }

    for row in rows:
        try:
            year, month, day = _parse_bs_date(row.bs_date)
            converted_ad = bs_to_gregorian(year, month, day).isoformat()
        except (TypeError, ValueError) as exc:
            report["invalid_dates"].append(_row_issue(row, str(exc)))
            continue

        provenance = get_bs_year_provenance(year)
        workflow_lower = row.workflow_type.lower()
        sensitive = any(token in workflow_lower for token in REVIEW_SENSITIVE_WORKFLOWS)

        if row.actual_ad_date and row.actual_ad_date != converted_ad:
            report["working_day_mismatches"].append(
                _row_issue(
                    row,
                    "actual_ad_date does not match Parva BS/AD conversion",
                    expected_ad_date=converted_ad,
                    actual_ad_date=row.actual_ad_date,
                )
            )

        if row.expected_behavior == "review_required" or sensitive:
            report["review_required_cases"].append(
                _row_issue(
                    row,
                    "workflow requires human review before operational use",
                    source_status=provenance.source_status,
                )
            )

        if provenance.confidence != "official":
            report["unsupported_future_assumptions"].append(
                _row_issue(
                    row,
                    "date is outside structured official public range used by this audit",
                    source_status=provenance.source_status,
                )
            )

        if row.holiday_assumption and "unknown" in row.holiday_assumption.lower():
            report["source_conflicts"].append(
                _row_issue(row, "holiday assumption is unknown or unsupported by provided evidence")
            )

        if row.fiscal_assumption and row.fiscal_assumption != "nepal_fiscal_year":
            report["fiscal_cutoff_errors"].append(
                _row_issue(row, "fiscal assumption is not the Nepal fiscal-year convention")
            )

    issue_count = sum(
        len(report[key])
        for key in (
            "invalid_dates",
            "holiday_mismatches",
            "working_day_mismatches",
            "fiscal_cutoff_errors",
            "unsupported_future_assumptions",
            "source_conflicts",
            "review_required_cases",
        )
    )
    max_penalty = max(len(rows), 1) * 2
    score = max(0.0, 100.0 - (issue_count / max_penalty) * 100.0)
    report["summary"]["conformance_score"] = round(score, 2)
    report["summary"]["issue_count"] = issue_count
    report["recommendations"] = _recommendations(report)
    return report


def _recommendations(report: dict[str, Any]) -> list[str]:
    recommendations = []
    if report["invalid_dates"]:
        recommendations.append("Reject invalid BS dates before persistence or conversion.")
    if report["working_day_mismatches"]:
        recommendations.append("Reconcile stored AD dates against deterministic BS/AD conversion.")
    if report["unsupported_future_assumptions"]:
        recommendations.append("Treat unsupported future or unverified source ranges as review_required.")
    if report["source_conflicts"]:
        recommendations.append("Attach source evidence for holiday and institution-specific assumptions.")
    if report["review_required_cases"]:
        recommendations.append("Require human review for sensitive payroll, repayment, banking, legal, or tax workflows.")
    if not recommendations:
        recommendations.append("No critical issues found in this sample. Keep source metadata attached.")
    return recommendations


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Vendor Date Risk Audit Report",
        "",
        "This is a technical conformance report, not certification and not official authority.",
        "",
        "## Summary",
        "",
        f"- Rows: {report['summary']['rows']}",
        f"- Conformance score: {report['summary']['conformance_score']}",
        f"- Issue count: {report['summary']['issue_count']}",
        "- Claim boundary: technical_conformance_report_not_certification",
        "",
    ]
    for key, title in (
        ("invalid_dates", "Invalid Dates"),
        ("holiday_mismatches", "Holiday Mismatches"),
        ("working_day_mismatches", "Working-Day Mismatches"),
        ("fiscal_cutoff_errors", "Fiscal Cutoff Errors"),
        ("unsupported_future_assumptions", "Unsupported Future Assumptions"),
        ("source_conflicts", "Source Conflicts"),
        ("review_required_cases", "Review-Required Cases"),
    ):
        lines.extend([f"## {title}", ""])
        items = report[key]
        if not items:
            lines.extend(["None.", ""])
            continue
        for item in items:
            lines.append(f"- Row {item['row_number']} `{item['bs_date']}`: {item['reason']}")
        lines.append("")
    lines.extend(["## Recommendations", ""])
    lines.extend(f"- {item}" for item in report["recommendations"])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def run_audit(input_path: Path, json_out: Path, md_out: Path) -> dict[str, Any]:
    report = audit_rows(_load_rows(input_path))
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, md_out)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--json-out", required=True, type=Path)
    parser.add_argument("--md-out", required=True, type=Path)
    args = parser.parse_args(argv)
    report = run_audit(args.input, args.json_out, args.md_out)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
