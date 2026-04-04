"""Kundali graph API for interactive SVG rendering."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.explainability import create_reason_trace
from app.services.kundali_graph_service import build_kundali_graph

from ._personal_utils import (
    CoordinateInput,
    base_meta_payload,
    normalize_coordinates,
    normalize_timezone,
    parse_datetime,
)

router = APIRouter(prefix="/api/kundali", tags=["kundali"])


class KundaliGraphRequest(BaseModel):
    datetime: str = Field(..., description="ISO8601 datetime")
    lat: CoordinateInput = Field(None, description="Latitude")
    lon: CoordinateInput = Field(None, description="Longitude")
    tz: Optional[str] = Field("Asia/Kathmandu", description="IANA timezone")


def _build_kundali_graph_response(
    *,
    datetime_str: str,
    lat: CoordinateInput,
    lon: CoordinateInput,
    tz: Optional[str],
):
    latitude, longitude, coord_warnings = normalize_coordinates(lat, lon)
    timezone_name, tz_warnings = normalize_timezone(tz)
    birth_dt = parse_datetime(datetime_str, tz_name=timezone_name)

    payload = build_kundali_graph(
        birth_dt=birth_dt,
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
    )

    trace = create_reason_trace(
        trace_type="kundali_graph",
        subject={"datetime": birth_dt.isoformat()},
        inputs={
            "datetime": birth_dt.isoformat(),
            "lat": latitude,
            "lon": longitude,
            "tz": timezone_name,
        },
        outputs={
            "house_nodes": len(payload.get("layout", {}).get("house_nodes", [])),
            "graha_nodes": len(payload.get("layout", {}).get("graha_nodes", [])),
            "aspect_edges": len(payload.get("layout", {}).get("aspect_edges", [])),
        },
        steps=[
            {"step": "kundali", "detail": "Computed D1 graph source from planetary positions."},
            {
                "step": "layout",
                "detail": "Mapped houses/grahas into deterministic SVG coordinates.",
            },
            {"step": "insights", "detail": "Generated plain-language insight blocks for sidebar."},
        ],
    )

    return {
        **payload,
        "warnings": coord_warnings + tz_warnings,
        **base_meta_payload(
            trace_id=trace["trace_id"],
            confidence="computed",
            method="swiss_ephemeris_sidereal",
            method_profile="kundali_graph_v1_svg",
            quality_band="validated",
            assumption_set_id="np-kundali-v2",
            advisory_scope="astrology_assist",
        ),
    }


@router.get("/graph")
async def kundali_graph_endpoint(
    datetime_str: str = Query(..., alias="datetime", description="ISO8601 datetime"),
    lat: Optional[str] = Query(None, description="Latitude"),
    lon: Optional[str] = Query(None, description="Longitude"),
    tz: Optional[str] = Query("Asia/Kathmandu", description="IANA timezone"),
):
    return _build_kundali_graph_response(datetime_str=datetime_str, lat=lat, lon=lon, tz=tz)


@router.post("/graph")
async def kundali_graph_endpoint_post(payload: KundaliGraphRequest):
    return _build_kundali_graph_response(
        datetime_str=payload.datetime,
        lat=payload.lat,
        lon=payload.lon,
        tz=payload.tz,
    )
