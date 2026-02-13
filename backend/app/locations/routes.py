"""
Locations API Routes
====================

Endpoints for temples and festival locations.
"""

from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from . import repository
from .models import Temple, TempleSummary


router = APIRouter(prefix="/api/temples", tags=["locations"])


class TempleListResponse(BaseModel):
    """Response for temple list."""
    temples: List[TempleSummary]
    total: int


class TempleWithRole(BaseModel):
    """Temple with its role for a festival."""
    temple: Temple
    role: Optional[str] = None


class TempleFestivalsResponse(BaseModel):
    """Response for festivals at a temple."""
    temple_id: str
    temple_name: str
    festival_ids: List[str]


@router.get("", response_model=TempleListResponse)
async def list_temples(
    festival: Optional[str] = Query(None, description="Filter by festival ID"),
    min_lat: Optional[float] = Query(None, description="Minimum latitude"),
    min_lng: Optional[float] = Query(None, description="Minimum longitude"),
    max_lat: Optional[float] = Query(None, description="Maximum latitude"),
    max_lng: Optional[float] = Query(None, description="Maximum longitude"),
):
    """
    List all temples.
    
    Can filter by:
    - festival: Get temples for a specific festival
    - bounds: Get temples within geographic bounds (all 4 params required)
    """
    if festival:
        temples = repository.get_temples_by_festival(festival)
        summaries = [
            TempleSummary(
                id=t.id,
                name=t.name,
                name_ne=t.name_ne,
                type=t.type,
                deity=t.deity,
                coordinates=t.coordinates,
                festival_count=len(t.festivals),
                festivals=t.festivals,
            )
            for t in temples
        ]
    elif all(v is not None for v in [min_lat, min_lng, max_lat, max_lng]):
        temples = repository.get_temples_in_bounds(min_lat, min_lng, max_lat, max_lng)
        summaries = [
            TempleSummary(
                id=t.id,
                name=t.name,
                name_ne=t.name_ne,
                type=t.type,
                deity=t.deity,
                coordinates=t.coordinates,
                festival_count=len(t.festivals),
                festivals=t.festivals,
            )
            for t in temples
        ]
    else:
        summaries = repository.get_temple_summaries()
    
    return TempleListResponse(temples=summaries, total=len(summaries))


@router.get("/{temple_id}", response_model=Temple)
async def get_temple(temple_id: str):
    """Get detailed information about a specific temple."""
    temple = repository.get_temple_by_id(temple_id)
    if not temple:
        raise HTTPException(status_code=404, detail=f"Temple '{temple_id}' not found")
    return temple


@router.get("/{temple_id}/festivals", response_model=TempleFestivalsResponse)
async def get_temple_festivals(temple_id: str):
    """Get list of festivals celebrated at a temple."""
    temple = repository.get_temple_by_id(temple_id)
    if not temple:
        raise HTTPException(status_code=404, detail=f"Temple '{temple_id}' not found")
    
    festival_ids = repository.get_festivals_at_temple(temple_id)
    return TempleFestivalsResponse(
        temple_id=temple_id,
        temple_name=temple.name,
        festival_ids=festival_ids
    )


@router.get("/for-festival/{festival_id}")
async def get_temples_for_festival(festival_id: str):
    """
    Get all temples with their roles for a specific festival.
    """
    temples = repository.get_temples_by_festival(festival_id)
    
    result = []
    for t in temples:
        role = repository.get_location_role(festival_id, t.id)
        result.append({
            "temple": {
                "id": t.id,
                "name": t.name,
                "name_ne": t.name_ne,
                "type": t.type,
                "deity": t.deity,
                "coordinates": {
                    "lat": t.coordinates.lat,
                    "lng": t.coordinates.lng
                },
            },
            "role": role
        })
    
    return {"festival_id": festival_id, "temples": result, "total": len(result)}
