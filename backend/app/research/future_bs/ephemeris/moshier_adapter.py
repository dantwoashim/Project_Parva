"""Moshier fallback adapter.

The current deployment uses pyswisseph's built-in Moshier mode unless external
Swiss/JPL ephemeris files are configured. This adapter is kept distinct in the
model registry so confidence output can name the fallback honestly.
"""

from __future__ import annotations

from .swiss_adapter import SwissEphemerisAdapter


class MoshierAdapter(SwissEphemerisAdapter):
    def __init__(self):
        super().__init__()
        object.__setattr__(self, "name", "swiss_moshier")
        object.__setattr__(self, "version", "pyswisseph_builtin_moshier_lahiri")
        object.__setattr__(
            self,
            "notes",
            "Built-in Moshier fallback through pyswisseph; no external JPL kernel configured.",
        )
