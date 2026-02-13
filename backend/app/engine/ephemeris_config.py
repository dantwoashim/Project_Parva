"""Central ephemeris configuration used by engine and API metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import swisseph as swe

Ayanamsa = Literal["lahiri", "raman", "kp"]
CoordinateSystem = Literal["sidereal", "tropical"]
EphemerisMode = Literal["moshier", "swiss"]

_AYANAMSA_MAP: dict[Ayanamsa, int] = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "kp": swe.SIDM_KRISHNAMURTI,
}


@dataclass(frozen=True)
class EphemerisConfig:
    """Runtime astronomy calculation knobs.

    Defaults are production-safe for current Parva behavior.
    """

    ayanamsa: Ayanamsa = "lahiri"
    coordinate_system: CoordinateSystem = "sidereal"
    ephemeris_mode: EphemerisMode = "moshier"

    @property
    def ayanamsa_code(self) -> int:
        return _AYANAMSA_MAP[self.ayanamsa]

    @property
    def header_value(self) -> str:
        return f"{self.ephemeris_mode}-{self.ayanamsa}-{self.coordinate_system}"


_ACTIVE_CONFIG = EphemerisConfig()


def get_ephemeris_config() -> EphemerisConfig:
    """Return active ephemeris configuration."""
    return _ACTIVE_CONFIG


def set_ephemeris_config(config: EphemerisConfig) -> EphemerisConfig:
    """Set active ephemeris configuration and return the new value."""
    global _ACTIVE_CONFIG
    _ACTIVE_CONFIG = config
    # Keep Swiss Ephemeris in sync for sidereal calculations.
    swe.set_sid_mode(config.ayanamsa_code)
    return _ACTIVE_CONFIG
