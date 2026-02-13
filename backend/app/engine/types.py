"""Typed contracts for the computation engine."""

from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

Confidence = Literal["exact", "computed", "estimated", "official", "astronomical"]


class EngineMeta(BaseModel):
    """Common metadata attached to engine outputs."""

    engine_version: str = "v2"
    method: str
    confidence: Confidence
    source: Optional[str] = None


class TithiResult(BaseModel):
    """Normalized tithi output contract."""

    number: int = Field(ge=1, le=30)
    display_number: int = Field(ge=1, le=15)
    paksha: Literal["shukla", "krishna"]
    name: str
    moon_phase: str
    meta: EngineMeta


class PanchangaResult(BaseModel):
    """Normalized panchanga output contract."""

    date: date
    tithi: dict
    nakshatra: dict
    yoga: dict
    karana: dict
    vaara: dict
    meta: EngineMeta


class ConversionResult(BaseModel):
    """Normalized date conversion contract."""

    from_calendar: Literal["gregorian", "bs"]
    to_calendar: Literal["gregorian", "bs"]
    input_date: str
    output_date: str
    meta: EngineMeta
    source_range: Optional[str] = None

    @model_validator(mode="after")
    def validate_estimated_has_range(self) -> "ConversionResult":
        """Require a range explanation for estimated conversions."""
        if self.meta.confidence == "estimated" and not self.source_range:
            raise ValueError("source_range is required when confidence='estimated'")
        return self


class FestivalDateResult(BaseModel):
    """Normalized festival-date contract."""

    festival_id: str
    start: date
    end: date
    duration_days: int = Field(ge=1)
    meta: EngineMeta
