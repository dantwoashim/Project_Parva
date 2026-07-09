"""Public alpha risk assessment for external future-BS assumptions."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from .labels import PUBLICATION_STATUS, RiskLabel
from .models import FutureBSRiskAssessment, FutureBSRiskInput
from .reason_codes import RiskReasonCode

PLAUSIBLE_MONTH_LENGTHS = {29, 30, 31, 32}
BOUNDARY_SENSITIVE_LENGTHS = {29, 32}
VALID_COMPLETE_YEAR_TOTALS = {365, 366}


def assess_month_assumption(assumption: FutureBSRiskInput) -> FutureBSRiskAssessment:
    """Classify an external month-length assumption without revealing a corrected value."""

    reasons: list[RiskReasonCode] = []
    notes: list[str] = []

    if assumption.synthetic_example:
        reasons.append(RiskReasonCode.SYNTHETIC_EXAMPLE)
        notes.append("Synthetic row used only to demonstrate public-safe audit shape.")

    if assumption.bs_month < 1 or assumption.bs_month > 12:
        return FutureBSRiskAssessment(
            bs_year=assumption.bs_year,
            bs_month=assumption.bs_month,
            risk_label=RiskLabel.RED,
            reason_codes=[*reasons, RiskReasonCode.NON_CLAIMABLE],
            source_policy=assumption.source_policy,
            review_required=True,
            high_risk=True,
            notes=[*notes, "BS month must be between 1 and 12."],
        )

    if assumption.month_length not in PLAUSIBLE_MONTH_LENGTHS:
        return FutureBSRiskAssessment(
            bs_year=assumption.bs_year,
            bs_month=assumption.bs_month,
            risk_label=RiskLabel.RED,
            reason_codes=[*reasons, RiskReasonCode.INVALID_MONTH_LENGTH, RiskReasonCode.NON_CLAIMABLE],
            source_policy=assumption.source_policy,
            review_required=True,
            high_risk=True,
            notes=[*notes, "Month assumption is outside the public risk review envelope."],
        )

    if assumption.month_length in BOUNDARY_SENSITIVE_LENGTHS:
        return FutureBSRiskAssessment(
            bs_year=assumption.bs_year,
            bs_month=assumption.bs_month,
            risk_label=RiskLabel.YELLOW,
            reason_codes=[*reasons, RiskReasonCode.BOUNDARY_SENSITIVE, RiskReasonCode.REVIEW_RECOMMENDED],
            source_policy=assumption.source_policy,
            boundary_sensitive=True,
            review_required=True,
            notes=[*notes, "Boundary-sensitive month length should be reviewed before operational use."],
        )

    return FutureBSRiskAssessment(
        bs_year=assumption.bs_year,
        bs_month=assumption.bs_month,
        risk_label=RiskLabel.GREEN,
        reason_codes=[*reasons, RiskReasonCode.LOW_RISK_CURRENT_CHECKS],
        source_policy=assumption.source_policy,
        notes=notes,
    )


def aggregate_blinded_audit(
    assumptions: Iterable[FutureBSRiskInput],
) -> dict[str, object]:
    """Return aggregate-only blinded audit metrics.

    Agreement means the supplied assumption is compatible with the public risk
    alpha and does not require review. It is not a corrected-value match.
    """

    assumption_list = list(assumptions)
    assessments = [assess_month_assumption(assumption) for assumption in assumption_list]
    year_totals: dict[int, int] = defaultdict(int)
    year_months: dict[int, set[int]] = defaultdict(set)
    for assumption in assumption_list:
        year_totals[assumption.bs_year] += assumption.month_length
        year_months[assumption.bs_year].add(assumption.bs_month)

    anomalous_years = {
        year
        for year, months in year_months.items()
        if len(months) == 12 and year_totals[year] not in VALID_COMPLETE_YEAR_TOTALS
    }

    disagreement_distribution: dict[str, int] = defaultdict(int)
    agreement_count = 0
    high_risk_month_count = 0
    boundary_sensitive_count = 0
    risk_label_distribution: dict[str, int] = defaultdict(int)

    for assessment in assessments:
        year_has_total_anomaly = assessment.bs_year in anomalous_years
        label = RiskLabel.RED if year_has_total_anomaly else assessment.risk_label
        risk_label_distribution[label.value] += 1

        if assessment.boundary_sensitive:
            boundary_sensitive_count += 1
        if label == RiskLabel.RED or assessment.high_risk:
            high_risk_month_count += 1
        if label == RiskLabel.GREEN:
            agreement_count += 1
        else:
            disagreement_distribution[str(assessment.bs_year)] += 1

    total = len(assessments)
    disagreement_count = total - agreement_count

    return {
        "publication_status": PUBLICATION_STATUS,
        "audit_mode": "blinded_aggregate",
        "agreement_definition": "compatible_with_public_risk_alpha_not_a_private_value_match",
        "total_months_checked": total,
        "agreement_count": agreement_count,
        "disagreement_count": disagreement_count,
        "disagreement_distribution_by_year": dict(sorted(disagreement_distribution.items())),
        "boundary_sensitive_count": boundary_sensitive_count,
        "year_total_anomaly_count": len(anomalous_years),
        "high_risk_month_count": high_risk_month_count,
        "risk_label_distribution": dict(sorted(risk_label_distribution.items())),
        "corrected_values_included": False,
    }
