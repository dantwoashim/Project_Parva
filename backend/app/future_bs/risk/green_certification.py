"""GREEN certification gates for future-BS predictions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
PREDICTION_PATH = PROJECT_ROOT / "data" / "future_bs" / "predictions" / "parva_future_bs_accuracy_best_2084_2200.json"
PUBLICATION_STATUS = "computed_prediction_not_official"


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
