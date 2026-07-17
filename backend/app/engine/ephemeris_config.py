"""Central ephemeris configuration used by engine and API metadata."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Literal

import swisseph as swe

from app.engine.swiss_state import SWISS_EPHEMERIS_LOCK

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
    with SWISS_EPHEMERIS_LOCK:
        return _ACTIVE_CONFIG


def set_ephemeris_config(config: EphemerisConfig) -> EphemerisConfig:
    """Set active ephemeris configuration and return the new value."""
    global _ACTIVE_CONFIG
    with SWISS_EPHEMERIS_LOCK:
        _ACTIVE_CONFIG = config
        swe.set_sid_mode(config.ayanamsa_code)
        return _ACTIVE_CONFIG


@contextmanager
def ephemeris_config_scope(config: EphemerisConfig) -> Iterator[EphemerisConfig]:
    """Apply one immutable profile for an entire synchronized calculation."""

    global _ACTIVE_CONFIG
    with SWISS_EPHEMERIS_LOCK:
        previous = _ACTIVE_CONFIG
        _ACTIVE_CONFIG = config
        swe.set_sid_mode(config.ayanamsa_code)
        try:
            yield config
        finally:
            _ACTIVE_CONFIG = previous
            swe.set_sid_mode(previous.ayanamsa_code)
