"""Shared synchronization for pyswisseph process-global state."""

from threading import RLock

SWISS_EPHEMERIS_LOCK = RLock()

__all__ = ["SWISS_EPHEMERIS_LOCK"]
