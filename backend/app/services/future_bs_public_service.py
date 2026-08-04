"""Public, read-only Future BS forecast snapshots and methodology metadata."""

from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.source_metadata import (
    PUBLIC_FUTURE_BS_FORECAST,
    RESEARCH_BOUNDARY,
    build_claim_meta,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_DATA_DIR = PROJECT_ROOT / "data" / "future_bs" / "public"
FORECAST_SNAPSHOT_PATH = PUBLIC_DATA_DIR / "forecast_snapshot_v6_2084_2200.json"
METHODOLOGY_PATH = PUBLIC_DATA_DIR / "selected_model_v6.json"
PUBLICATION_STATUS = "computed_prediction_not_official"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required public Future BS artifact is missing: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("publication_status") != PUBLICATION_STATUS:
        raise RuntimeError(f"Public Future BS artifact has an invalid publication status: {path.name}")
    return payload


@lru_cache(maxsize=1)
def _forecast_snapshot() -> dict[str, Any]:
    payload = _load_json(FORECAST_SNAPSHOT_PATH)
    years = payload.get("years")
    if not isinstance(years, dict) or not years:
        raise RuntimeError("Public Future BS forecast snapshot contains no years.")
    return payload


@lru_cache(maxsize=1)
def _methodology() -> dict[str, Any]:
    return _load_json(METHODOLOGY_PATH)


def _claim_meta(*, trace_id: str | None, result_class: str) -> dict[str, Any]:
    meta = build_claim_meta(
        source=PUBLIC_FUTURE_BS_FORECAST,
        confidence="computed_research",
        claim_boundary=RESEARCH_BOUNDARY,
        trace_id=trace_id,
        warnings=[
            PUBLICATION_STATUS,
            "human_review_required_before_operational_use",
            "later_authoritative_publication_overrides_this_forecast",
        ],
        result_class=result_class,
    )
    meta["maturity"] = "research_preview"
    return meta


def _forecast_range(snapshot: dict[str, Any]) -> dict[str, int]:
    forecast_range = snapshot.get("forecast_range") or {}
    return {
        "start_bs_year": int(forecast_range["start_bs_year"]),
        "end_bs_year": int(forecast_range["end_bs_year"]),
    }


def future_bs_capabilities_payload(*, trace_id: str | None = None) -> dict[str, Any]:
    snapshot = _forecast_snapshot()
    methodology = _methodology()
    meta = _claim_meta(trace_id=trace_id, result_class="future_bs_public_capability")
    return {
        "surface": "future_bs_public_research",
        "status": "research_preview",
        "maturity": "research_preview",
        "publication_status": PUBLICATION_STATUS,
        "review_required": True,
        "claim_boundary": meta["claim_boundary"],
        "confidence": meta["confidence"],
        "release_id": meta["release_id"],
        "warnings": meta["warnings"],
        "forecast_range": _forecast_range(snapshot),
        "method_version": snapshot["method_version"],
        "model_id": methodology["model_id"],
        "validation": deepcopy(snapshot["validation"]),
        "meta": meta,
        "public_surface": [
            "single_year_month_length_forecast",
            "month_prediction_sets",
            "civil_boundary_distance",
            "risk_label_taxonomy",
            "selected_methodology",
            "validation_posture",
        ],
        "public_endpoints": [
            "/v4/api/future-bs/capabilities",
            "/v4/api/future-bs/methodology",
            "/v4/api/future-bs/forecast/{bs_year}",
        ],
        "controlled_surfaces": [
            "bulk_forecast_export",
            "external_sheet_import_and_comparison",
            "model_run_registry",
            "financial_impact_simulation",
            "private_source_material",
        ],
        "not_claimed": [
            "official_future_publication",
            "legal_or_tax_final_authority",
            "guaranteed_future_calendar_accuracy",
            "independent_99_percent_accuracy",
        ],
        "not_authority": (
            "The public forecast is computed research, not an official future calendar, "
            "legal decision, tax ruling, payroll approval, or banking-contract authority."
        ),
    }


def future_bs_methodology_payload(*, trace_id: str | None = None) -> dict[str, Any]:
    payload = deepcopy(_methodology())
    payload.update(
        {
            "surface": "future_bs_public_methodology",
            "review_required": True,
            "meta": _claim_meta(trace_id=trace_id, result_class="future_bs_public_methodology"),
        }
    )
    return payload


def future_bs_forecast_payload(bs_year: int, *, trace_id: str | None = None) -> dict[str, Any]:
    snapshot = _forecast_snapshot()
    forecast_range = _forecast_range(snapshot)
    if bs_year < forecast_range["start_bs_year"] or bs_year > forecast_range["end_bs_year"]:
        raise ValueError(
            "bs_year must be within the public research forecast range "
            f"{forecast_range['start_bs_year']}-{forecast_range['end_bs_year']}."
        )

    year_payload = snapshot["years"].get(str(bs_year))
    if not isinstance(year_payload, dict):
        raise ValueError(f"No public research forecast is available for BS year {bs_year}.")

    result = deepcopy(year_payload)
    risk_counts = {"GREEN": 0, "YELLOW": 0, "RED": 0}
    for month in result["months"]:
        risk_label = str(month["risk_label"]).upper()
        risk_counts[risk_label] = risk_counts.get(risk_label, 0) + 1

    result.update(
        {
            "surface": "future_bs_public_forecast",
            "status": "research_preview",
            "maturity": "research_preview",
            "publication_status": PUBLICATION_STATUS,
            "review_required": True,
            "authoritative_publication_overrides": True,
            "snapshot_id": snapshot["snapshot_id"],
            "method": {
                "model_id": snapshot["model_id"],
                "method_version": snapshot["method_version"],
                "calibration_version": snapshot["calibration_version"],
                "model_family": result.pop("model_family"),
                "model_subfamily": result.pop("model_subfamily"),
            },
            "risk_summary": risk_counts,
            "validation": deepcopy(snapshot["validation"]),
            "limits": {
                **forecast_range,
                "forecast_kind": "precomputed_research_snapshot",
                "official_publication_required_for_final_use": True,
            },
            "meta": _claim_meta(trace_id=trace_id, result_class="future_bs_public_forecast"),
        }
    )
    return result


__all__ = [
    "PUBLICATION_STATUS",
    "future_bs_capabilities_payload",
    "future_bs_forecast_payload",
    "future_bs_methodology_payload",
]
