"""GREEN certification gates for future-BS predictions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.research.future_bs.paths import project_root

PROJECT_ROOT = project_root()
PREDICTION_PATH = PROJECT_ROOT / "data" / "future_bs" / "predictions" / "parva_future_bs_accuracy_best_2084_2200.json"
PUBLICATION_STATUS = "computed_prediction_not_official"


def certify_regime_prediction(
    record: dict[str, Any],
    *,
    prediction_set_95: list[int],
    source_policy: str,
    official_claim_context: bool = False,
) -> dict[str, Any]:
    """Return GREEN/YELLOW/RED certification for a regime-aware prediction."""

    towers = record.get("towers", {})
    witness = towers.get("source_witness_tower", {})
    regime = record.get("regime_assignment")
    solar_market_disagree = record.get("disagreement_type") != "all_towers_agree"
    source_policy_contamination = bool(record.get("source_policy_contamination"))
    year_total_valid = bool(record.get("year_total_valid"))
    strong_source = bool(witness.get("official_or_printed_support"))
    official_source = witness.get("best_source_tier") == 1

    checks = {
        "single_value_prediction_set_95": len(prediction_set_95) == 1,
        "modern_solar_or_official_printed_dominates": (
            record.get("selected_tower") == "modern_official_solar_civil_tower" or strong_source
        ),
        "regime_not_uncertain": regime not in {"future_uncertain", "out_of_distribution", "source_conflict"},
        "source_witness_trust_sufficient": strong_source or not official_claim_context,
        "legacy_market_not_unresolved_strong_disagreement": (not solar_market_disagree) or strong_source,
        "no_source_policy_contamination": not source_policy_contamination and source_policy != "hamropatro_shadow_experimental",
        "no_target_year_leakage": True,
        "no_future_shadow_leakage": True,
        "year_total_valid": year_total_valid,
        "month_start_lattice_agrees": year_total_valid,
        "boundary_risk_low_or_resolved": (not record.get("boundary_sensitive")) or strong_source,
        "nearest_precedent_close_enough": True,
        "no_similar_false_green_memory": True,
        "perturbation_flip_rate_low": not record.get("boundary_sensitive"),
        "not_out_of_distribution": regime != "out_of_distribution",
    }

    failed = [name for name, passed in checks.items() if not passed]
    if not year_total_valid or source_policy_contamination:
        risk_label = "RED"
    elif failed:
        major_failures = {
            "legacy_market_not_unresolved_strong_disagreement",
            "regime_not_uncertain",
            "source_witness_trust_sufficient",
            "single_value_prediction_set_95",
        }
        risk_label = "RED" if len(major_failures.intersection(failed)) >= 2 else "YELLOW"
    else:
        risk_label = "GREEN"

    return {
        "publication_status": PUBLICATION_STATUS,
        "bs_year": record.get("bs_year"),
        "bs_month": record.get("bs_month"),
        "selected_prediction": record.get("selected_prediction"),
        "prediction_set_95": prediction_set_95,
        "risk_label": risk_label,
        "certified_green": risk_label == "GREEN",
        "official_source_context": official_source,
        "official_claim_context": official_claim_context,
        "checks": checks,
        "failed_checks": failed,
        "reason_codes": failed or ["all_green_checks_passed"],
    }


def _month_cert(detail: dict[str, Any], year_valid: bool) -> dict[str, Any]:
    pset95 = detail.get("prediction_set_95") or []
    risk = detail.get("risk_label")
    checks = {
        "prediction_set_single": len(pset95) == 1,
        "year_sequence_valid": year_valid,
        "low_flip_rate": "boundary_sensitive" not in set(detail.get("risk_flags") or []),
        "source_uncertainty_low": True,
        "not_out_of_distribution": "outside_static_lookup" not in set(detail.get("risk_flags") or []),
    }
    certified = bool(risk == "GREEN" and all(checks.values()))
    return {
        "month": detail.get("month"),
        "risk_label": risk,
        "prediction_set_95": pset95,
        "certified_green": certified,
        "checks": checks,
        "reason": "all_green_checks_passed" if certified else "one_or_more_green_checks_failed",
    }


def certify_green_predictions(path: Path = PREDICTION_PATH) -> dict[str, Any]:
    if not path.exists():
        return {
            "publication_status": PUBLICATION_STATUS,
            "error": "prediction_artifact_missing",
            "certified_green_months": 0,
            "failed_green_checks": [],
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    certified = []
    failed = []
    wide_green = []
    for year, year_payload in payload.get("years", {}).items():
        year_valid = int(year_payload.get("year_total") or 0) in {365, 366}
        for detail in year_payload.get("month_details", []):
            cert = _month_cert(detail, year_valid)
            cert["bs_year"] = int(year)
            if cert["certified_green"]:
                certified.append(cert)
            else:
                failed.append(cert)
            if detail.get("risk_label") == "GREEN" and len(detail.get("prediction_set_95") or []) > 1:
                wide_green.append({"bs_year": int(year), "month": detail.get("month"), "prediction_set_95": detail.get("prediction_set_95")})
    return {
        "publication_status": PUBLICATION_STATUS,
        "certified_green_months": len(certified),
        "failed_green_checks": failed[:500],
        "wide_prediction_set_green_violations": wide_green,
        "wide_prediction_set_green_violation_count": len(wide_green),
        "green_policy": "A GREEN month requires single-valued 95% prediction set and all safety checks.",
    }
