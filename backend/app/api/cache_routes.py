"""Cache/precompute inspection endpoints (Year 3 Week 17-20)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.cache import (
    get_cache_stats,
    load_precomputed_festival_year,
    load_precomputed_panchanga,
    measure_hotset_latency,
)

router = APIRouter(prefix="/api/cache", tags=["cache"])


@router.get("/stats")
async def cache_stats():
    stats = get_cache_stats()
    panchanga_years = sorted(
        int(f["name"].replace("panchanga_", "").replace(".json", ""))
        for f in stats["files"]
        if f["name"].startswith("panchanga_")
    )
    festival_years = sorted(
        int(f["name"].replace("festivals_", "").replace(".json", ""))
        for f in stats["files"]
        if f["name"].startswith("festivals_")
    )
    stats["years"] = {
        "panchanga": panchanga_years,
        "festivals": festival_years,
    }
    stats["coverage"] = {
        "panchanga_year_count": len(panchanga_years),
        "festival_year_count": len(festival_years),
        "shared_years": sorted(set(panchanga_years) & set(festival_years)),
        "panchanga_only_years": sorted(set(panchanga_years) - set(festival_years)),
        "festival_only_years": sorted(set(festival_years) - set(panchanga_years)),
    }
    stats["hotset_latency"] = measure_hotset_latency()
    return stats


@router.get("/panchanga/{year}/{month}/{day}")
async def cache_lookup_panchanga(year: int, month: int, day: int):
    from datetime import date

    try:
        d = date(year, month, day)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date") from exc
    payload = load_precomputed_panchanga(d)
    if not payload:
        raise HTTPException(status_code=404, detail="Precomputed panchanga not found")
    return payload


@router.get("/festivals/{year}")
async def cache_lookup_festivals(year: int):
    payload = load_precomputed_festival_year(year)
    if not payload:
        raise HTTPException(status_code=404, detail="Precomputed festival year not found")
    return payload
