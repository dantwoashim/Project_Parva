"""Date-risk audit workflow."""

from __future__ import annotations

from datetime import date

from app.calendar.bikram_sambat import bs_to_gregorian
from app.membranes.capsule import (
    build_fiscal_year_capsule,
    build_holiday_capsule,
    build_validate_bs_date_capsule,
    build_working_day_capsule,
)
from app.membranes.proofpack import proof_pack
from app.membranes.timepack import verify_timepack
from app.sources.hashing import canonical_json_hash

DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
KNOWN_INPUT_COLUMNS = {
    "bs_date",
    "actual_ad_date",
    "ad_date",
    "workflow_type",
    "holiday_assumption",
    "source_status",
    "claimed_authority",
    "employee_id",
    "notes",
}


def _clean(value: object | None) -> str:
    return str(value or "").strip().translate(DEVANAGARI_DIGITS)


def _split_bs_date(bs_date: str) -> tuple[int, int, int]:
    parts = _clean(bs_date).replace("/", "-").split("-")
    if len(parts) != 3:
        raise ValueError("BS date must be YYYY-MM-DD")
    year, month, day = (int(part) for part in parts)
    return year, month, day


def _parse_ad_date(value: str) -> date:
    return date.fromisoformat(_clean(value))


def _severity(issues: list[str]) -> str:
    if any(issue in issues for issue in ("invalid_bs_date", "invalid_ad_date", "missing_bs_date")):
        return "high"
    if any(issue in issues for issue in ("bs_ad_mismatch", "unsupported_range", "static_reference_overclaim")):
        return "medium"
    if issues:
        return "low"
    return "none"


def audit_date_rows(rows: list[dict], *, include_proofs: bool = False) -> list[dict]:
    results = []
    seen_keys: set[tuple[str, str]] = set()
    for index, row in enumerate(rows, start=1):
        original_row = dict(row)
        row = {str(key).strip(): _clean(value) for key, value in row.items()}
        bs_date = row.get("bs_date", "")
        expected_ad = row.get("actual_ad_date") or row.get("ad_date")
        issues: list[str] = []
        diagnostics: list[str] = []
        proof_packs: list[dict] = []
        ad_date = None
        key = (bs_date, expected_ad or "")
        if key in seen_keys and any(key):
            issues.append("duplicate_row")
        seen_keys.add(key)
        unknown_columns = sorted(set(row) - KNOWN_INPUT_COLUMNS)
        if unknown_columns:
            diagnostics.append(f"unknown_columns:{','.join(unknown_columns)}")
        if not bs_date:
            issues.append("missing_bs_date")
        try:
            if not bs_date:
                raise ValueError("missing BS date")
            year, month, day = _split_bs_date(bs_date)
            validate_membrane = build_validate_bs_date_capsule(year, month, day)
            ad_date = bs_to_gregorian(year, month, day).isoformat()
            holiday_membrane = build_holiday_capsule(year, month, day)
            working_membrane = build_working_day_capsule(year, month, day)
            fiscal_membrane = build_fiscal_year_capsule(year)
            if include_proofs:
                proof_packs.extend(
                    [
                        proof_pack(validate_membrane, "replay"),
                        proof_pack(holiday_membrane, "replay"),
                        proof_pack(working_membrane, "replay"),
                        proof_pack(fiscal_membrane, "replay"),
                    ]
                )
            if expected_ad:
                try:
                    parsed_expected = _parse_ad_date(expected_ad).isoformat()
                except ValueError:
                    parsed_expected = None
                    issues.append("invalid_ad_date")
                if parsed_expected and parsed_expected != ad_date:
                    issues.append("bs_ad_mismatch")
            if year > 2083:
                issues.append("unsupported_range")
            if year >= 2084:
                issues.append("review_required_future_sensitive")
            if month == 4 and day in {1, 31, 32}:
                issues.append("fiscal_boundary_ambiguity")
            if str(row.get("source_status", "")).lower() in {"verified", "official", "source_backed"}:
                issues.append("static_reference_overclaim")
            if str(row.get("claimed_authority", "")).lower() in {"payroll_authority", "legal_authority"}:
                issues.append("authority_overclaim")
            if expected_ad and expected_ad != ad_date and "invalid_ad_date" not in issues:
                issues.append("bs_ad_mismatch")
            if holiday_membrane["result"].get("is_holiday"):
                issues.append("holiday_conflict")
            if not working_membrane["result"].get("is_working_day"):
                issues.append("non_working_day_conflict")
        except (ValueError, OverflowError):
            ad_date = None
            if "missing_bs_date" not in issues:
                issues.append("invalid_bs_date")
            if expected_ad:
                try:
                    _parse_ad_date(expected_ad)
                except ValueError:
                    issues.append("invalid_ad_date")
        if str(row.get("workflow_type", "")).startswith("future"):
            issues.append("review_required_future_sensitive")
        if row.get("holiday_assumption") == "assume_no_holidays":
            issues.append("holiday_assumption_requires_review")
        issues = sorted(set(issues))
        results.append(
            {
                "row_number": index,
                "original_row": original_row,
                "bs_date": bs_date,
                "expected_ad_date": expected_ad or None,
                "ad_date": ad_date,
                "status": "review_required" if issues else "pass",
                "issues": issues,
                "diagnostics": diagnostics,
                "severity": _severity(issues),
                "risk_score": min(100, len(issues) * 25),
                "fix_suggestions": ["manual_review"] if issues else [],
                "claim_boundary": "payroll_date_risk_not_authority",
                "proof_packs": proof_packs if include_proofs else [],
            }
        )
    return results


def build_date_risk_timepack(rows: list[dict]) -> dict:
    audited = audit_date_rows(rows, include_proofs=True)
    proof_packs = [pack for result in audited for pack in result["proof_packs"]]
    child_hashes = [pack["witness_hash"] for pack in proof_packs]
    return {
        "kind": "parva_timepack",
        "timepack_version": "v1",
        "artifact_type": "payroll_date_risk_audit",
        "proof_packs": proof_packs,
        "aggregate_witness_hash": f"sha256:{canonical_json_hash(child_hashes)}",
        "boundary_summary": {
            "not_authority": True,
            "review_required": any(result["status"] == "review_required" for result in audited),
            "claim_boundary": "payroll_date_risk_not_authority",
        },
        "result_summary": {
            "rows": len(audited),
            "review_required": sum(1 for result in audited if result["status"] == "review_required"),
            "findings": audited,
        },
        "replay_instructions": "Run `parva verify-timepack <path>` from a checkout with committed proof fixtures.",
    }


def verify_date_risk_timepack(timepack: dict) -> tuple[bool, str]:
    return verify_timepack(timepack)
