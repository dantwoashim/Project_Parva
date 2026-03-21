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

    trace = create_reason_trace(
        trace_type="place_search",
        subject={"query": query},
        inputs={"q": query, "limit": limit},
        outputs={"count": payload.get("total", 0)},
        steps=[
            {"step": "geocoding", "detail": "Resolved place candidates via OpenStreetMap Nominatim."},
            {"step": "timezone", "detail": "Attached timezone per candidate from coordinate lookup."},
            {"step": "normalize", "detail": "Returned normalized place labels and coordinates for form use."},
        ],
    )

    return {
        **payload,
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="nominatim_place_search",
            method_profile="place_search_v1",
            quality_band="validated",
            assumption_set_id="global-place-search-v1",
            advisory_scope="form_input",
        ),
    }


__all__ = ["router"]
