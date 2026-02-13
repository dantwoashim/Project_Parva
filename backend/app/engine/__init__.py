"""Engine package exports.

Keep imports lightweight to avoid circular dependencies with calendar modules.
"""

from .ephemeris_config import EphemerisConfig, get_ephemeris_config, set_ephemeris_config
from .interface import EngineInterface
from .time_utils import ensure_utc, to_npt, from_npt
from .types import EngineMeta, TithiResult, PanchangaResult, ConversionResult, FestivalDateResult


def get_default_engine():
    """Lazy-load the default engine implementation."""
    from .core_engine import ParvaEngine

    return ParvaEngine()


__all__ = [
    "EngineInterface",
    "get_default_engine",
    "EphemerisConfig",
    "get_ephemeris_config",
    "set_ephemeris_config",
    "ensure_utc",
    "to_npt",
    "from_npt",
    "EngineMeta",
    "TithiResult",
    "PanchangaResult",
    "ConversionResult",
    "FestivalDateResult",
]
