"""Safe JPL SPICE-style adapter facade for optional research kernels."""

from __future__ import annotations

import swisseph as swe

from .jpl_de440_adapter import _SWISSEPH_LOCK, JPLDe440Adapter


class JPLSpiceAdapter(JPLDe440Adapter):
    """DE440-backed adapter with solar and lunar longitude helpers.

    The project currently uses pyswisseph's JPL bridge rather than a direct
    SpiceyPy dependency. This facade keeps the public contract explicit while
    preserving unavailable behavior when the operator has not configured a
    kernel.
    """

    def __init__(self, kernel_path: str | None = None):
        super().__init__(kernel_path=kernel_path)
        object.__setattr__(self, "name", "jpl_spice_de440")
        object.__setattr__(self, "version", "de440_spk_swe_bridge")

    def apparent_lunar_longitude(self, jd_tdb: float) -> float:
        kernel = self._require_kernel()
        with _SWISSEPH_LOCK:
            swe.set_ephe_path(str(kernel.parent))
            swe.set_jpl_file(kernel.name)
            position, _ = swe.calc(jd_tdb, swe.MOON, swe.FLG_JPLEPH)
        return float(position[0] % 360.0)

    def sidereal_lunar_longitude(self, jd_tdb: float, ayanamsha: str) -> float:
        kernel = self._require_kernel()
        flags = swe.FLG_JPLEPH | swe.FLG_SIDEREAL
        mode = {
            "lahiri": swe.SIDM_LAHIRI,
            "chitra_paksha": swe.SIDM_LAHIRI,
            "raman": swe.SIDM_RAMAN,
            "krishnamurti": swe.SIDM_KRISHNAMURTI,
        }.get(ayanamsha.lower())
        if mode is None:
            raise ValueError(f"Unsupported JPL sidereal ayanamsha: {ayanamsha}")
        with _SWISSEPH_LOCK:
            swe.set_ephe_path(str(kernel.parent))
            swe.set_jpl_file(kernel.name)
            swe.set_sid_mode(mode, 0, 0)
            position, _ = swe.calc(jd_tdb, swe.MOON, flags)
        return float(position[0] % 360.0)
