"""Calendar VaR and no-break schedule policy helpers."""

from __future__ import annotations

from typing import Any


def calendar_var_payload(payload: dict[str, Any], *, prediction: dict[str, Any]) -> dict[str, Any]:
    month = int(payload.get("month", 1))
    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12.")
    detail = prediction["month_details"][month - 1]
    principal = float(payload.get("principal", 0.0))
    annual_rate = float(payload.get("annual_rate", 0.0))
    affected_contracts = int(payload.get("affected_contracts", 1))
    irreversibility = float(payload.get("operational_irreversibility_score", 1.0))
    publication_delay = float(payload.get("official_publication_delay_risk", 1.0))
    mismatch_probability = max(0.0, min(1.0, 1.0 - float(detail.get("confidence_score", 0.0))))
    one_day_interest = principal * (annual_rate / 100.0) / 365.0
    score = mismatch_probability * one_day_interest * affected_contracts * irreversibility * publication_delay
    risk = "low"
    if score >= 1_000_000 or mismatch_probability > 0.15:
        risk = "high"
    elif score >= 100_000 or mismatch_probability > 0.05:
        risk = "medium"
    return {
        "bs_year": prediction["bs_year"],
        "month": month,
        "month_name": detail["month_name"],
        "parva_prediction": detail["final_days"],
        "mismatch_probability": round(mismatch_probability, 4),
        "affected_contracts": affected_contracts,
        "estimated_one_day_interest_exposure": round(one_day_interest * affected_contracts, 2),
        "calendar_risk_score": round(score, 2),
        "operational_risk": risk,
        "recommended_policy": (
            "dual_schedule_until_official_publication"
            if risk in {"medium", "high"}
            else "normal_computed_schedule_with_reconciliation_marker"
        ),
        "stress_scenarios": [
            "Parva prediction correct",
            "official month plus one day",
            "official month minus one day",
            "official publication late",
            "contracts signed before correction",
            "EMI schedule already generated",
            "interest already accrued",
        ],
    }
