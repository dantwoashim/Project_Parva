from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest
from app.engine.ephemeris_config import get_ephemeris_config
from app.panchanga.ephemeris_provider import BuiltInApproxProvider

TARGET_DATE = date(2026, 2, 6)
LATITUDE = 27.7172
LONGITUDE = 85.3240
TIMEZONE = "Asia/Kathmandu"


def _profile_result(ayanamsa: str) -> tuple[str, float, float]:
    result = BuiltInApproxProvider().panchanga_for(
        TARGET_DATE,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        timezone_name=TIMEZONE,
        ayanamsa=ayanamsa,
    )
    return result["ayanamsa"], result["sun"]["longitude"], result["moon"]["longitude"]


def test_requested_ayanamsa_is_effective_and_reported() -> None:
    lahiri = _profile_result("lahiri")
    raman = _profile_result("raman")
    kp = _profile_result("kp")

    assert lahiri[0] == "lahiri"
    assert raman[0] == "raman"
    assert kp[0] == "kp"
    assert len({lahiri[1], raman[1], kp[1]}) == 3
    assert len({lahiri[2], raman[2], kp[2]}) == 3


def test_profile_scope_restores_active_configuration() -> None:
    before = get_ephemeris_config()

    _profile_result("raman")

    assert get_ephemeris_config() == before


def test_profile_scope_is_deterministic_under_concurrency() -> None:
    expected = {mode: _profile_result(mode) for mode in ("lahiri", "raman", "kp")}
    requested = ["lahiri", "raman", "kp"] * 8

    with ThreadPoolExecutor(max_workers=8) as executor:
        observed = list(executor.map(_profile_result, requested))

    assert observed == [expected[mode] for mode in requested]


def test_unknown_ayanamsa_fails_closed() -> None:
    with pytest.raises(ValueError, match="unsupported ayanamsa"):
        _profile_result("unknown")
