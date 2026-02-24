"""
Festival Data Models
====================

Pydantic models for festival data, including mythology, rituals,
locations, and API responses.
"""

from __future__ import annotations

from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class LocationLink(BaseModel):
    """Reference to a temple or location."""
    id: str
    name: str
    role: Optional[str] = None  # e.g., "main temple", "pilgrimage start"
    coordinates: Optional[tuple[float, float]] = None


class RitualStep(BaseModel):
    """A step in a ritual sequence."""
    order: int = Field(..., ge=1)
    name: str
    name_nepali: Optional[str] = None
    description: str
    time_of_day: Optional[str] = None  # e.g., "morning", "evening", "midnight"
    duration: Optional[str] = None  # e.g., "30 minutes", "all day"
    location: Optional[str] = None
    items_needed: Optional[List[str]] = None
    significance: Optional[str] = None


class DayRituals(BaseModel):
    """Rituals for a specific day of a multi-day festival."""
    day: int = Field(..., ge=1)
    name: str
    name_nepali: Optional[str] = None
    description: str
    rituals: List[RitualStep] = Field(default_factory=list)
    is_main_day: bool = False


class DeityLink(BaseModel):
    """Reference to a deity associated with a festival."""
    id: str
    name: str
    name_nepali: Optional[str] = None
    role: Optional[str] = None  # e.g., "primary deity", "invoked during puja"


class MythologyContent(BaseModel):
    """Mythological/origin story content for a festival."""
    summary: str = Field(..., min_length=50)
    origin_story: Optional[str] = None  # Full narrative (800-1000 words for priority festivals)
    legends: Optional[List[str]] = None  # Additional legends
    scriptural_references: Optional[List[str]] = None
    historical_context: Optional[str] = None
    regional_variations: Optional[Dict[str, str]] = None  # region -> variation


class ProvenanceMeta(BaseModel):
    """Provenance metadata for response verification."""
    dataset_hash: Optional[str] = None
    rules_hash: Optional[str] = None
    snapshot_id: Optional[str] = None
    verify_url: Optional[str] = None


class FestivalDates(BaseModel):
    """Calculated dates for a festival in a specific year."""
    gregorian_year: int
    bs_year: int
    start_date: date
    end_date: date
    duration_days: int
    days_until: Optional[int] = None  # Days from today
    provenance: Optional[ProvenanceMeta] = None


class Festival(BaseModel):
    """Complete festival data model."""
    
    # Core Identity
    id: str = Field(..., pattern=r"^[a-z0-9-]+$")
    name: str
    name_nepali: Optional[str] = None
    name_local: Optional[str] = None  # Alternative local names
    
    # Classification
    calendar_type: str = Field(default="lunar")  # lunar, solar, hybrid
    category: str  # national, newari, regional, buddhist, hindu
    significance_level: int = Field(default=2, ge=1, le=5)  # 1=minor, 5=major
    
    # Brief Description
    tagline: str = Field(..., max_length=200)  # Short memorable description
    description: str  # 2-3 paragraph description
    
    # Timing
    typical_month_bs: Optional[int] = None  # 1-12
    typical_month_gregorian: Optional[str] = None  # e.g., "September-October"
    duration_days: int = Field(default=1, ge=1)
    
    # Content Depth (for priority festivals)
    mythology: Optional[MythologyContent] = None
    daily_rituals: Optional[List[DayRituals]] = None
    simple_rituals: Optional[List[RitualStep]] = None  # For single-day festivals
    ritual_sequence: Optional[Dict[str, Any]] = None  # Canonical UI shape: {days: [...]}
    
    # Connections
    deities: Optional[List[DeityLink]] = None  # Detailed deity info (future use)
    connected_deities: Optional[List[str]] = None  # Simple deity name list for display
    locations: Optional[List[LocationLink]] = None
    related_festivals: Optional[List[str]] = None  # IDs of related festivals
    
    # Observance
    who_celebrates: Optional[str] = None  # e.g., "All Hindus", "Newari community"
    is_national_holiday: bool = False
    regional_focus: Optional[List[str]] = None  # e.g., ["Kathmandu Valley", "Bhaktapur"]
    
    # Visual/Media
    primary_color: Optional[str] = None  # Hex color for theming
    icon: Optional[str] = None  # Icon identifier
    images: Optional[List[str]] = None  # Image URLs/paths
    
    # Metadata
    content_status: str = Field(default="minimal")  # minimal, basic, complete
    sources: Optional[List[str]] = None
    last_updated: Optional[date] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "dashain",
                "name": "Dashain",
                "name_nepali": "दशैं",
                "calendar_type": "lunar",
                "category": "national",
                "significance_level": 5,
                "tagline": "Nepal's greatest festival celebrating victory of good over evil",
                "description": "Dashain is the longest and most significant festival in Nepal...",
                "typical_month_bs": 6,
                "typical_month_gregorian": "September-October",
                "duration_days": 15,
                "is_national_holiday": True,
                "content_status": "complete"
            }
        }
    )


class FestivalSummary(BaseModel):
    """Condensed festival info for list views."""
    id: str
    name: str
    name_nepali: Optional[str] = None
    tagline: str
    category: str
    duration_days: int
    significance_level: int
    is_national_holiday: bool
    primary_color: Optional[str] = None

    # Rule quality metadata
    rule_status: Optional[str] = None
    rule_family: Optional[str] = None
    validation_band: Optional[str] = None
    source_evidence_ids: List[str] = Field(default_factory=list)

    # Next occurrence (computed)
    next_start: Optional[date] = None
    next_end: Optional[date] = None
    days_until: Optional[int] = None


class FestivalListResponse(BaseModel):
    """API response for festival list."""
    festivals: List[FestivalSummary]
    total: int
    page: int = 1
    page_size: int = 50
    provenance: Optional[ProvenanceMeta] = None


class FestivalDetailResponse(BaseModel):
    """API response for single festival detail."""
    festival: Festival
    dates: Optional[FestivalDates] = None
    nearby_festivals: Optional[List[FestivalSummary]] = None
    provenance: Optional[ProvenanceMeta] = None


class FestivalExplainResponse(BaseModel):
    """Human-readable explanation of computed festival date."""
    festival_id: str
    festival_name: str
    year: int
    start_date: date
    end_date: date
    method: str
    confidence: str
    rule_summary: str
    explanation: str
    steps: List[str]
    calculation_trace_id: str
    provenance: Optional[ProvenanceMeta] = None


class UpcomingFestival(BaseModel):
    """Festival in upcoming festivals list."""
    id: str
    name: str
    name_nepali: Optional[str] = None
    tagline: str
    category: str
    start_date: date
    end_date: date
    days_until: int
    duration_days: int
    primary_color: Optional[str] = None
    rule_status: Optional[str] = None
    rule_family: Optional[str] = None
    validation_band: Optional[str] = None
    source_evidence_ids: List[str] = Field(default_factory=list)


class UpcomingFestivalsResponse(BaseModel):
    """API response for upcoming festivals."""
    festivals: List[UpcomingFestival]
    from_date: date
    to_date: date
    total: int
    provenance: Optional[ProvenanceMeta] = None


class CalendarDayFestivals(BaseModel):
    """Festivals on a specific calendar day."""
    date: date
    bs_date: Optional[str] = None  # Formatted BS date
    festivals: List[FestivalSummary]
    moon_phase: Optional[str] = None
    tithi: Optional[int] = None
    paksha: Optional[str] = None


class FestivalCalendarResponse(BaseModel):
    """API response for calendar view."""
    days: List[CalendarDayFestivals]
    month: int
    year: int
    provenance: Optional[ProvenanceMeta] = None
