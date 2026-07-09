"""Swiss Ephemeris adapter."""

from __future__ import annotations

from app.calendar.ephemeris.swiss_eph import get_sun_longitude

from .base import EphemerisAdapter
from .time_scales import jd_tdb_to_jd_ut_approx, jd_ut_to_utc_datetime


class SwissEphemerisAdapter(EphemerisAdapter):
    def __init__(self):
        super().__init__(
            name="swiss_ephemeris",
            version="pyswisseph_lahiri",
            available=True,
            notes="Swiss Ephemeris via pyswisseph, configured with Lahiri sidereal mode.",
        )

    def apparent_solar_longitude(self, jd_tdb: float) -> float:
        dt = jd_ut_to_utc_datetime(jd_tdb_to_jd_ut_approx(jd_tdb))
        return get_sun_longitude(dt, sidereal=False)

    def sidereal_solar_longitude(self, jd_tdb: float, ayanamsha: str) -> float:
        dt = jd_ut_to_utc_datetime(jd_tdb_to_jd_ut_approx(jd_tdb))
        # Current production adapter supports Lahiri through the shared ephemeris config.
        # Additional ayanamsha names are evaluated at the model layer as sensitivity
        # candidates until explicit Swiss sidereal mode switching is wired per call.
        return get_sun_longitude(dt, sidereal=True)
