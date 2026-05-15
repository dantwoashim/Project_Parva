"""Base ephemeris adapter contract."""

from __future__ import annotations

from dataclasses import dataclass


class EphemerisUnavailableError(RuntimeError):
    """Raised when an optional ephemeris backend is not configured."""


@dataclass(frozen=True)
class EphemerisAdapter:
    name: str
    version: str
    available: bool = True
    notes: str = ""

    def apparent_solar_longitude(self, jd_tdb: float) -> float:
        raise NotImplementedError

    def sidereal_solar_longitude(self, jd_tdb: float, ayanamsha: str) -> float:
        raise NotImplementedError

    def payload(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "available": self.available,
            "notes": self.notes,
        }

    def status(self) -> dict:
        return self.payload()
