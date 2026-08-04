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
ISSUE_CATEGORIES = (
    "invalid_dates",
    "holiday_mismatches",
    "working_day_mismatches",
    "fiscal_cutoff_errors",
    "unsupported_future_assumptions",
    "source_conflicts",
)


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


def _regression_call(bs_date: str) -> str:
    year, month, day = _parse_bs_date(bs_date)
    return f"bs_to_gregorian({year}, {month}, {day})"


def _finding_details(category: str, item: dict[str, Any]) -> dict[str, str]:
    if category == "invalid_dates":
        return {
            "severity": "critical",
            "title": "Invalid BS date reaches a business workflow",
            "observed": item["reason"],
            "expected": "Reject the value before persistence, conversion, or workflow execution.",
            "consequence": "The affected payroll or invoice workflow can fail or store an impossible civil date.",
            "remediation": "Validate BS year, month, and day against the canonical month-length row at the input boundary.",
            "regression_test": f"with pytest.raises(ValueError):\n    {_regression_call(item['bs_date'])}",
        }
    if category == "working_day_mismatches":
        return {
            "severity": "high",
            "title": "Stored AD and BS dates identify different civil days",
            "observed": f"Vendor AD value is {item['actual_ad_date']}.",
            "expected": f"{item['bs_date']} converts to {item['expected_ad_date']}.",
            "consequence": "Invoices, attendance, due dates, and sorted reports can move by one day.",
            "remediation": "Correct the stored AD value and enforce conversion plus round-trip checks before persistence.",
            "regression_test": (
                f"assert {_regression_call(item['bs_date'])}.isoformat() "
                f"== \"{item['expected_ad_date']}\""
            ),
        }
    if category == "fiscal_cutoff_errors":
        return {
            "severity": "high",
            "title": "Workflow uses the wrong fiscal-year convention",
            "observed": f"Fiscal assumption is {item['fiscal_assumption']}.",
            "expected": "Use the configured Nepal fiscal-year convention for the audited workflow.",
            "consequence": "Transactions can be assigned to the wrong reporting year at the Shrawan boundary.",
            "remediation": "Resolve fiscal periods through the shared fiscal engine instead of calendar-year logic.",
            "regression_test": (
                "assert fiscal_period_for_bs_date(2082, 4, 1).fiscal_year_label "
                "== \"2082/83\""
            ),
        }
    if category == "unsupported_future_assumptions":
        return {
            "severity": "high",
            "title": "Future date is treated beyond the official source range",
            "observed": f"Source status is {item['source_status']} for {item['bs_date']}.",
            "expected": "Require an authoritative source or keep the result explicitly review-required.",
            "consequence": "A repayment or contractual date can appear final before an authoritative calendar is published.",
            "remediation": "Persist source status and block operational finalization until the authoritative release is available.",
            "regression_test": (
                f"assert get_bs_year_provenance({item['bs_date'].split('-', 1)[0]}).confidence "
                "!= \"official\""
            ),
        }
    if category == "source_conflicts":
        return {
            "severity": "medium",
            "title": "Holiday policy lacks a supported source",
            "observed": f"Holiday assumption is {item['holiday_assumption']}.",
            "expected": "Attach a named source release and institution policy to the decision.",
            "consequence": "The workflow can skip or include the wrong working day without an auditable reason.",
            "remediation": "Require source ID, release ID, and institution profile before holiday adjustment.",
            "regression_test": "assert audit_report[\"source_conflicts\"]",
        }
    if category == "review_required_cases":
        return {
            "severity": "advisory",
            "title": "Sensitive workflow requires human approval",
            "observed": f"{item['workflow_type']} uses source status {item['source_status']}.",
            "expected": "Hold final execution until a reviewer accepts the source and policy context.",
            "consequence": "Automatic execution would bypass the stated control for a sensitive workflow.",
            "remediation": "Enforce a review-required state and record reviewer identity, decision, and timestamp.",
            "regression_test": "assert audit_report[\"review_required_cases\"]",
        }
    return {
        "severity": "medium",
        "title": category.replace("_", " ").title(),
        "observed": item["reason"],
        "expected": "Match the configured source and policy.",
        "consequence": "The workflow can produce a date decision that differs from its declared policy.",
        "remediation": "Reconcile the row against the configured source and add a regression case.",
        "regression_test": "assert audited_result == expected_result",
    }


def _build_findings(report: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    categories = (*ISSUE_CATEGORIES, "review_required_cases")
    for category in categories:
        for item in report[category]:
            details = _finding_details(category, item)
            findings.append(
                {
                    "finding_id": f"PARVA-AUD-{len(findings) + 1:03d}",
                    "category": category,
                    **details,
                    "row_number": item["row_number"],
                    "bs_date": item["bs_date"],
                    "workflow_type": item["workflow_type"],
                }
            )
    return findings


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
        "findings": [],
        "regression_tests": [],
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
                _row_issue(
                    row,
                    "holiday assumption is unknown or unsupported by provided evidence",
                    holiday_assumption=row.holiday_assumption,
                )
            )

        if row.fiscal_assumption and row.fiscal_assumption != "nepal_fiscal_year":
            report["fiscal_cutoff_errors"].append(
                _row_issue(
                    row,
                    "fiscal assumption is not the Nepal fiscal-year convention",
                    fiscal_assumption=row.fiscal_assumption,
                )
            )

    issue_count = sum(len(report[key]) for key in ISSUE_CATEGORIES)
    max_penalty = max(len(rows), 1) * 2
    score = max(0.0, 100.0 - (issue_count / max_penalty) * 100.0)
    report["summary"]["conformance_score"] = round(score, 2)
    report["summary"]["issue_count"] = issue_count
    report["summary"]["review_control_count"] = len(report["review_required_cases"])
    report["summary"]["affected_rows"] = len(
        {item["row_number"] for key in ISSUE_CATEGORIES for item in report[key]}
    )
    report["findings"] = _build_findings(report)
    report["regression_tests"] = [
        {
            "finding_id": finding["finding_id"],
            "test": finding["regression_test"],
        }
        for finding in report["findings"]
    ]
    report["summary"]["severity_counts"] = {
        severity: sum(1 for finding in report["findings"] if finding["severity"] == severity)
        for severity in ("critical", "high", "medium", "advisory")
    }
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
        "# Parva Vendor Date Risk Audit - Demonstration Report",
        "",
        "This sanitized demonstration shows the audit deliverable for a software vendor. It is a technical conformance report, not certification or official authority.",
        "",
        "## Executive Summary",
        "",
        f"- Rows: {report['summary']['rows']}",
        f"- Rows with failures: {report['summary']['affected_rows']}",
        f"- Conformance score: {report['summary']['conformance_score']}",
        f"- Technical failures: {report['summary']['issue_count']}",
        f"- Review controls: {report['summary']['review_control_count']}",
        f"- Critical findings: {report['summary']['severity_counts']['critical']}",
        f"- High findings: {report['summary']['severity_counts']['high']}",
        "",
        "The screening score subtracts one half-row penalty for each technical failure and floors at zero. Review controls are reported separately and do not reduce the score.",
        "",
        "The sample contains an impossible BS month, a one-day dual-date mismatch, an unsupported future-date assumption, a source gap, and a fiscal-policy mismatch. Correct boundary rows are included to show that the audit distinguishes passing cases from failures.",
        "",
        "## Finding Index",
        "",
        "| ID | Severity | Category | BS date | Workflow |",
        "| --- | --- | --- | --- | --- |",
    ]
    for finding in report["findings"]:
        lines.append(
            f"| {finding['finding_id']} | {finding['severity'].upper()} | "
            f"{finding['category'].replace('_', ' ')} | `{finding['bs_date']}` | "
            f"{finding['workflow_type']} |"
        )
    lines.extend(
        [
            "",
            "## Detailed Findings",
            "",
            "Runnable equivalents are provided in `regression_test_sample.py`.",
            "",
        ]
    )
    for finding in report["findings"]:
        lines.extend(
            [
                f"### {finding['finding_id']}: {finding['title']}",
                "",
                f"- Severity: {finding['severity'].upper()}",
                f"- Input: row {finding['row_number']}, `{finding['bs_date']}`, `{finding['workflow_type']}`",
                f"- Observed: {finding['observed']}",
                f"- Expected: {finding['expected']}",
                f"- Consequence: {finding['consequence']}",
                f"- Required fix: {finding['remediation']}",
                "- Regression check:",
                "",
                "```python",
                finding["regression_test"],
                "```",
                "",
            ]
        )
    lines.extend(["## Remediation Order", ""])
    lines.extend(f"- {item}" for item in report["recommendations"])
    lines.extend(
        [
            "",
            "## Acceptance Criteria",
            "",
            "- Every critical and high regression check passes in CI.",
            "- Stored AD and BS values round-trip to the same civil day.",
            "- Invalid dates are rejected before persistence.",
            "- Future and source-limited decisions remain review-required.",
            "- Fiscal periods resolve through the configured Nepal fiscal policy.",
            "",
        ]
    )
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
