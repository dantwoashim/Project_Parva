"""Date-risk audit workflow."""

from __future__ import annotations

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


def _split_bs_date(bs_date: str) -> tuple[int, int, int]:
    year, month, day = (int(part) for part in bs_date.split("-"))
    return year, month, day


def audit_date_rows(rows: list[dict], *, include_proofs: bool = False) -> list[dict]:
    results = []
    for row in rows:
        bs_date = row["bs_date"]
        issues: list[str] = []
        proof_packs: list[dict] = []
        try:
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
            expected_ad = row.get("actual_ad_date")
            if expected_ad and expected_ad != ad_date:
                issues.append("bs_ad_mismatch")
            if holiday_membrane["result"].get("is_holiday"):
                issues.append("holiday_conflict")
            if not working_membrane["result"].get("is_working_day"):
                issues.append("non_working_day_conflict")
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
