"""Optional JPL DE440 adapter placeholder.

The adapter is intentionally explicit: without a configured kernel, it reports
unavailable instead of pretending DE440 is active.
"""

from __future__ import annotations

import os

from .base import EphemerisAdapter, EphemerisUnavailableError


class JPLDe440Adapter(EphemerisAdapter):
    def __init__(self, kernel_path: str | None = None):
        self.kernel_path = kernel_path or os.getenv("PARVA_JPL_DE440_KERNEL")
        super().__init__(
            name="jpl_de440",
            version="de440_optional_kernel",
            available=bool(self.kernel_path),
            notes=(
                "Configured JPL DE440 kernel."
                if self.kernel_path
                else "Set PARVA_JPL_DE440_KERNEL to enable DE440 calculations."
            ),
        )

    def _raise_unavailable(self) -> None:
        raise EphemerisUnavailableError(
            "JPL DE440 kernel is not configured. Set PARVA_JPL_DE440_KERNEL before using this adapter."
        )

    def apparent_solar_longitude(self, jd_tdb: float) -> float:
        self._raise_unavailable()

    def sidereal_solar_longitude(self, jd_tdb: float, ayanamsha: str) -> float:
        self._raise_unavailable()
