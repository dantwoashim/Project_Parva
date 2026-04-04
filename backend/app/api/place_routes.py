"""Place search routes for birth-chart and planning inputs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.explainability import create_reason_trace
from app.services import search_places

from ._personal_utils import base_meta_payload

router = APIRouter(prefix="/api/places", tags=["places"])


@router.get("/search")
async def place_search(
    query: str = Query(..., alias="q", min_length=2, max_length=120, description="Place search query"),
    limit: int = Query(5, ge=1, le=8, description="Maximum number of place candidates"),
):
    try:
        payload = search_places(query=query, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    payload.setdefault("source_mode", "remote_geocoder")
    payload.setdefault(
        "privacy_notice",
        "Place queries are sent to the configured geocoding provider for resolution.",
    )
    payload.setdefault(
        "service_notice",
        "For privacy-sensitive or high-volume deployments, prefer an offline gazetteer over the public upstream service.",
    )
    source_mode = payload.get("source_mode") or "remote_geocoder"
    method = (
        "offline_nepal_gazetteer_search"
        if source_mode == "offline_gazetteer"
        else "nominatim_place_search"
    )
    trace_steps = []
    if source_mode == "offline_gazetteer":
        trace_steps.append(
            {
                "step": "local_search",
                "detail": "Resolved place candidates from the bundled offline Nepal gazetteer.",
            }
        )
        trace_steps.append(
            {
                "step": "normalize",
                "detail": "Returned local place labels, coordinates, and timezone for privacy-preserving form use.",
            }
        )
    else:
        trace_steps.append(
            {"step": "geocoding", "detail": "Resolved place candidates via OpenStreetMap Nominatim."}
        )
        trace_steps.append(
            {"step": "timezone", "detail": "Attached timezone per candidate from coordinate lookup."}
        )
        trace_steps.append(
            {"step": "normalize", "detail": "Returned normalized place labels and coordinates for form use."}
        )

    trace = create_reason_trace(
        trace_type="place_search",
        subject={"query": query},
        inputs={"q": query, "limit": limit},
        outputs={"count": payload.get("total", 0)},
        steps=trace_steps,
    )

    return {
        **payload,
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method=method,
            method_profile="place_search_v1",
            quality_band="validated",
            assumption_set_id="global-place-search-v1",
            advisory_scope="form_input",
        ),
    }


__all__ = ["router"]
