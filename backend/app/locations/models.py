"""
Locations Models
================

Data models for temples and festival locations.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """Geographic coordinates."""
    lat: float
    lng: float


class Temple(BaseModel):
    """Temple or sacred location."""
    id: str
    name: str
    name_ne: Optional[str] = None
    type: str  # temple, stupa, heritage, shrine, ground
    deity: Optional[str] = None
    coordinates: Coordinates
    significance: Optional[str] = None
    festivals: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    visiting_hours: Optional[str] = None
    entry_fee: Optional[str] = None


class TempleSummary(BaseModel):
    """Summary view of temple for list displays."""
    id: str
    name: str
    name_ne: Optional[str] = None
    type: str
    deity: Optional[str] = None
    coordinates: Coordinates
    festival_count: int = 0
    festivals: List[str] = Field(default_factory=list)  # For map highlighting


class FestivalLocationMapping(BaseModel):
    """Mapping of festival to its locations."""
    festival_id: str
    primary_locations: List[str]
    roles: dict[str, str] = Field(default_factory=dict)
