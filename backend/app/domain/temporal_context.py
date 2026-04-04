"""Explicit context objects for temporal computation and presentation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Optional


@dataclass(frozen=True)
class LocationContext:
    """Normalized location payload shared across compute and trust layers."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone_name: Optional[str] = None
    source: str = "runtime"
    precision: str = "point"

    def as_dict(self) -> dict[str, Any]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone_name,
            "source": self.source,
            "precision": self.precision,
        }


@dataclass(frozen=True)
class CalendarContext:
    """Normalized calendar request context for a temporal surface."""

    target_date: date
    surface: str
    risk_mode: str = "standard"
    snapshot_id: Optional[str] = None
    support_tier: Optional[str] = None
    calendar_system: str = "gregorian"

    def as_dict(self) -> dict[str, Any]:
        return {
            "date": self.target_date.isoformat(),
            "surface": self.surface,
            "risk_mode": self.risk_mode,
            "snapshot_id": self.snapshot_id,
            "support_tier": self.support_tier,
            "calendar_system": self.calendar_system,
        }
