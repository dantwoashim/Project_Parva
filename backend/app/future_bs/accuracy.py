"""Month-level accuracy metrics and source-quality policy for future BS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

TARGET_THRESHOLDS = {
    "overall_top1_accuracy": 98.5,
    "green_zone_accuracy": 99.3,
    "green_zone_coverage": 90.0,
    "minimum_official_month_cases": 528,
}

TRAIN_ALLOWED_SOURCE_TYPES = {
    "official_verified",
    "printed_verified",
    "physical_patro_verified",
    "approved_patro",
}
TEST_ALLOWED_SOURCE_TYPES = {
    "official_verified",
    "printed_verified",
    "physical_patro_verified",
}
REFERENCE_ONLY_SOURCE_TYPES = {
    "third_party_reference",
    "scraped_reference",
    "needs_review",
}


@dataclass(frozen=True)
class AccuracyCase:
    bs_year: int
    month: int
    month_name: str
    predicted_days: int
    actual_days: int
    confidence_score: float
    risk_label: str
    boundary_risk: str
    risk_flags: list[str]
    source_type: str
    verification_status: str

    @property
    def passed(self) -> bool:
        return self.predicted_days == self.actual_days

    @property
    def is_green_zone(self) -> bool:
        return self.risk_label == "GREEN"

    @property
    def is_boundary_case(self) -> bool:
        return self.boundary_risk in {"high", "critical"}

    @property
    def boundary_flagged(self) -> bool:
        return bool(
            self.is_boundary_case
            and (
                "manual_review_recommended" in self.risk_flags
                or "sankranti_near_civil_assignment_boundary" in self.risk_flags
            )
        )

    def payload(self) -> dict[str, Any]:
        return {
            "bs_year": self.bs_year,
            "month": self.month,
            "month_name": self.month_name,
            "predicted_days": self.predicted_days,
            "actual_days": self.actual_days,
            "passed": self.passed,
            "confidence_score": self.confidence_score,
            "risk_label": self.risk_label,
            "boundary_risk": self.boundary_risk,
            "risk_flags": self.risk_flags,
            "source_type": self.source_type,
            "verification_status": self.verification_status,
        }


def source_quality_level(source_type: str, verification_status: str) -> int:
    if source_type == "official_verified" and verification_status == "verified":
        return 1
    if source_type in {"printed_verified", "physical_patro_verified", "approved_patro"}:
        return 2
    if source_type in {"internal_reference", "third_party_reference"}:
        return 3
    return 4


def source_allowed_for_training(source_type: str, verification_status: str) -> bool:
    if source_type == "official_verified":
        return verification_status == "verified"
    if source_type in {"printed_verified", "physical_patro_verified"}:
        return verification_status in {"verified", "reviewed"}
    if source_type == "approved_patro":
        return verification_status in {"verified", "reviewed"}
    return False


def source_allowed_for_final_test(source_type: str, verification_status: str) -> bool:
    if source_type == "official_verified":
        return verification_status == "verified"
    if source_type in {"printed_verified", "physical_patro_verified"}:
        return verification_status in {"verified", "reviewed"}
    return False


def source_policy_allows(source_type: str, verification_status: str, policy: str) -> bool:
    if policy == "all_reference":
        return True
    if policy == "official_only":
        return source_type == "official_verified" and verification_status == "verified"
    if policy == "official_plus_printed":
        return source_allowed_for_final_test(source_type, verification_status)
    if policy == "train_allowed":
        return source_allowed_for_training(source_type, verification_status)
    raise ValueError(
        "source_policy must be one of: all_reference, official_only, official_plus_printed, train_allowed"
    )


def risk_label(
    *,
    confidence_score: float,
    model_agreement_ratio: float,
    boundary_risk: str,
    risk_flags: list[str],
) -> str:
    if boundary_risk in {"critical", "high"}:
        return "RED"
    if "manual_review_recommended" in risk_flags or "model_disagreement" in risk_flags:
        return "YELLOW"
    if confidence_score >= 0.985 and model_agreement_ratio >= 0.86 and boundary_risk == "low":
        return "GREEN"
    if confidence_score >= 0.90 and boundary_risk in {"low", "medium"}:
        return "YELLOW"
    return "RED"


def _percent(numerator: int, denominator: int) -> float:
    return round((numerator / denominator) * 100, 2) if denominator else 0.0


def summarize_accuracy(cases: list[AccuracyCase], *, official_month_cases: int) -> dict[str, Any]:
    total = len(cases)
    passed = sum(case.passed for case in cases)
    green_cases = [case for case in cases if case.is_green_zone]
    green_passed = sum(case.passed for case in green_cases)
    boundary_cases = [case for case in cases if case.is_boundary_case]
    flagged_boundary = sum(case.boundary_flagged for case in boundary_cases)
    by_month: dict[int, dict[str, Any]] = {}
    for case in cases:
        bucket = by_month.setdefault(
            case.month,
            {
                "month": case.month,
                "month_name": case.month_name,
                "total": 0,
                "passed": 0,
                "accuracy": 0.0,
            },
        )
        bucket["total"] += 1
        bucket["passed"] += int(case.passed)
    for bucket in by_month.values():
        bucket["accuracy"] = _percent(int(bucket["passed"]), int(bucket["total"]))

    metrics = {
        "total_month_cases": total,
        "passed_month_cases": passed,
        "failed_month_cases": total - passed,
        "overall_top1_accuracy": _percent(passed, total),
        "green_zone_cases": len(green_cases),
        "green_zone_passed": green_passed,
        "green_zone_accuracy": _percent(green_passed, len(green_cases)),
        "green_zone_coverage": _percent(len(green_cases), total),
        "boundary_cases": len(boundary_cases),
        "boundary_cases_flagged": flagged_boundary,
        "boundary_case_accuracy": _percent(flagged_boundary, len(boundary_cases)),
        "mismatch_by_bs_month": [by_month[key] for key in sorted(by_month)],
        "target_thresholds": TARGET_THRESHOLDS,
    }
    metrics["claim_readiness"] = {
        "ready_for_99_percent_green_zone_claim": bool(
            official_month_cases >= TARGET_THRESHOLDS["minimum_official_month_cases"]
            and metrics["overall_top1_accuracy"] >= TARGET_THRESHOLDS["overall_top1_accuracy"]
            and metrics["green_zone_accuracy"] >= TARGET_THRESHOLDS["green_zone_accuracy"]
            and metrics["green_zone_coverage"] >= TARGET_THRESHOLDS["green_zone_coverage"]
        ),
        "official_month_cases": official_month_cases,
        "minimum_official_month_cases_required": TARGET_THRESHOLDS["minimum_official_month_cases"],
        "claim_boundary": (
            "Only use the 99%+ claim for source-strict official/printed cases and GREEN months "
            "after this readiness flag is true."
        ),
    }
    return metrics
