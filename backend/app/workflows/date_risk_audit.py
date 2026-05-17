"""Date-risk audit workflow."""

from __future__ import annotations

from app.calendar.bikram_sambat import bs_to_gregorian


def audit_date_rows(rows: list[dict]) -> list[dict]:
    results = []
    for row in rows:
        bs_date = row["bs_date"]
        issues: list[str] = []
        try:
            year, month, day = (int(part) for part in bs_date.split("-"))
            ad_date = bs_to_gregorian(year, month, day).isoformat()
        except ValueError:
            ad_date = None
            issues.append("invalid_bs_date")
        if str(row.get("workflow_type", "")).startswith("future"):
            issues.append("review_required_future_sensitive")
        if row.get("holiday_assumption") == "assume_no_holidays":
            issues.append("holiday_assumption_requires_review")
        results.append(
            {
                "bs_date": bs_date,
                "ad_date": ad_date,
                "status": "review_required" if issues else "pass",
                "issues": issues,
                "fix_suggestions": ["manual_review"] if issues else [],
                "claim_boundary": "payroll_date_risk_not_authority",
            }
        )
    return results
