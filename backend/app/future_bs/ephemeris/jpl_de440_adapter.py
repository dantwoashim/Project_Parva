"""JPL DE440 adapter backed by a configured NAIF SPK kernel."""

from __future__ import annotations

import os
from pathlib import Path
from threading import Lock

import swisseph as swe

from .base import EphemerisAdapter, EphemerisUnavailableError

_SWISSEPH_LOCK = Lock()

_SIDEREAL_MODES = {
    "lahiri": swe.SIDM_LAHIRI,
    "chitra_paksha": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
}


class JPLDe440Adapter(EphemerisAdapter):
    def __init__(self, kernel_path: str | None = None):
        configured = kernel_path or os.getenv("PARVA_JPL_DE440_KERNEL")
        self.kernel_path = Path(configured).expanduser() if configured else None
        available = bool(self.kernel_path and self.kernel_path.exists())
        super().__init__(
            name="jpl_de440",
            version="de440_spk",
            available=available,
            notes=(
                f"Configured JPL DE440-family SPK kernel: {self.kernel_path.name}."
                if available
                else "Set PARVA_JPL_DE440_KERNEL to an existing de440 .bsp file."
            ),
        )

    def _require_kernel(self) -> Path:
        if not self.kernel_path or not self.kernel_path.exists():
            raise EphemerisUnavailableError(
                "JPL DE440 kernel is not configured. Set PARVA_JPL_DE440_KERNEL to an existing .bsp file."
            )
        return self.kernel_path

    def _calc_longitude(self, jd_tdb: float, *, sidereal: bool, ayanamsha: str = "lahiri") -> float:
        kernel = self._require_kernel()
        flags = swe.FLG_JPLEPH
        if sidereal:
            mode = _SIDEREAL_MODES.get(ayanamsha.lower())
            if mode is None:
                raise ValueError(f"Unsupported JPL sidereal ayanamsha: {ayanamsha}")
            flags |= swe.FLG_SIDEREAL
        with _SWISSEPH_LOCK:
            swe.set_ephe_path(str(kernel.parent))
            swe.set_jpl_file(kernel.name)
            if sidereal:
                swe.set_sid_mode(mode, 0, 0)
            position, _ = swe.calc(jd_tdb, swe.SUN, flags)
        return float(position[0] % 360.0)

    def apparent_solar_longitude(self, jd_tdb: float) -> float:
        return self._calc_longitude(jd_tdb, sidereal=False)

    def sidereal_solar_longitude(self, jd_tdb: float, ayanamsha: str) -> float:
        return self._calc_longitude(jd_tdb, sidereal=True, ayanamsha=ayanamsha)
