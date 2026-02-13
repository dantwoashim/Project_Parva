"""Week 10 ayanamsa/config tests."""

from datetime import datetime, timezone

from app.engine.ephemeris_config import EphemerisConfig, get_ephemeris_config, set_ephemeris_config
from app.calendar.ephemeris.swiss_eph import get_sun_longitude, get_moon_longitude


def test_ayanamsa_changes_sidereal_longitude():
    dt = datetime(2026, 5, 10, 0, 0, tzinfo=timezone.utc)

    lahiri = EphemerisConfig(ayanamsa="lahiri", coordinate_system="sidereal", ephemeris_mode="moshier")
    raman = EphemerisConfig(ayanamsa="raman", coordinate_system="sidereal", ephemeris_mode="moshier")

    sun_lahiri = get_sun_longitude(dt, config=lahiri)
    sun_raman = get_sun_longitude(dt, config=raman)

    # Ayanamsa choices should produce a measurable difference.
    assert abs(sun_lahiri - sun_raman) > 0.1


def test_tropical_ignores_ayanamsa_choice():
    dt = datetime(2026, 5, 10, 0, 0, tzinfo=timezone.utc)

    lahiri_tropical = EphemerisConfig(ayanamsa="lahiri", coordinate_system="tropical", ephemeris_mode="moshier")
    raman_tropical = EphemerisConfig(ayanamsa="raman", coordinate_system="tropical", ephemeris_mode="moshier")

    moon1 = get_moon_longitude(dt, config=lahiri_tropical)
    moon2 = get_moon_longitude(dt, config=raman_tropical)

    assert abs(moon1 - moon2) < 1e-6


def test_set_get_global_ephemeris_config_roundtrip():
    original = get_ephemeris_config()
    custom = EphemerisConfig(ayanamsa="kp", coordinate_system="sidereal", ephemeris_mode="moshier")
    try:
        updated = set_ephemeris_config(custom)
        assert updated == custom
        assert get_ephemeris_config() == custom
    finally:
        set_ephemeris_config(original)
