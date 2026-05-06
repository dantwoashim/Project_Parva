"""Robust solar-ingress solver for sidereal sign boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from app.calendar.ephemeris.time_utils import to_nepal_time
from app.calendar.sankranti import BS_MONTH_NAMES, RASHI_NAMES

from .ephemeris import EphemerisAdapter, MoshierAdapter
from .ephemeris.time_scales import (
    jd_ut_to_jd_tdb_approx,
    jd_ut_to_utc_datetime,
    utc_datetime_to_jd_ut,
)

SOLVER_VERSION = "solar_ingress_solver_v1"
TARGET_LONGITUDES = [float(index * 30) for index in range(12)]


@dataclass(frozen=True)
class SolarIngressSolution:
    target_longitude: float
    sign: str
    bs_month: int
    bs_month_name: str
    utc_time: datetime
    nepal_time: datetime
    ephemeris: str
    ayanamsha: str
    calculation_version: str = SOLVER_VERSION

    def payload(self) -> dict[str, Any]:
        return {
            "target_longitude": int(self.target_longitude),
            "sign": self.sign,
            "bs_month": self.bs_month,
            "bs_month_name": self.bs_month_name,
            "utc_time": self.utc_time.isoformat().replace("+00:00", "Z"),
            "nepal_time": self.nepal_time.isoformat(),
            "ephemeris": self.ephemeris,
            "ayanamsha": self.ayanamsha,
            "calculation_version": self.calculation_version,
        }


def angular_error(value_deg: float, target_deg: float) -> float:
    return ((value_deg - target_deg + 180.0) % 360.0) - 180.0


def _longitude(adapter: EphemerisAdapter, jd_ut: float, ayanamsha: str) -> float:
    return adapter.sidereal_solar_longitude(jd_ut_to_jd_tdb_approx(jd_ut), ayanamsha)


def _f(adapter: EphemerisAdapter, jd_ut: float, target_longitude: float, ayanamsha: str) -> float:
    return angular_error(_longitude(adapter, jd_ut, ayanamsha), target_longitude)


def bracket_crossing(
    target_longitude: float,
    start_utc: datetime,
    *,
    adapter: EphemerisAdapter | None = None,
    ayanamsha: str = "lahiri",
    max_days: int = 40,
) -> tuple[float, float]:
    adapter = adapter or MoshierAdapter()
    start_utc = start_utc.astimezone(timezone.utc)
    previous_dt = start_utc
    previous_jd = utc_datetime_to_jd_ut(previous_dt)
    previous_error = _f(adapter, previous_jd, target_longitude, ayanamsha)
    for day_offset in range(1, max_days + 1):
        current_dt = start_utc + timedelta(days=day_offset)
        current_jd = utc_datetime_to_jd_ut(current_dt)
        current_error = _f(adapter, current_jd, target_longitude, ayanamsha)
        if previous_error == 0 or previous_error * current_error <= 0:
            return previous_jd, current_jd
        previous_jd = current_jd
        previous_error = current_error
    raise ValueError(f"Could not bracket solar ingress for {target_longitude} degrees.")


def solve_crossing_brent(
    target_longitude: float,
    low_jd_ut: float,
    high_jd_ut: float,
    *,
    adapter: EphemerisAdapter | None = None,
    ayanamsha: str = "lahiri",
    tolerance_seconds: int = 30,
    max_iterations: int = 60,
) -> float:
    adapter = adapter or MoshierAdapter()
    tolerance_days = tolerance_seconds / 86400.0
    a = low_jd_ut
    b = high_jd_ut
    fa = _f(adapter, a, target_longitude, ayanamsha)
    fb = _f(adapter, b, target_longitude, ayanamsha)
    if fa == 0:
        return a
    if fb == 0:
        return b
    if fa * fb > 0:
        raise ValueError("Solar ingress bracket does not contain a sign change.")
    c = a
    fc = fa
    d = a
    mflag = True
    for _ in range(max_iterations):
        if abs(b - a) <= tolerance_days or fb == 0:
            return b
        if fa != fc and fb != fc:
            s = (
                (a * fb * fc) / ((fa - fb) * (fa - fc))
                + (b * fa * fc) / ((fb - fa) * (fb - fc))
                + (c * fa * fb) / ((fc - fa) * (fc - fb))
            )
        else:
            s = b - fb * (b - a) / (fb - fa)
        cond1 = not (min((3 * a + b) / 4, b) < s < max((3 * a + b) / 4, b))
        cond2 = mflag and abs(s - b) >= abs(b - c) / 2
        cond3 = (not mflag) and abs(s - b) >= abs(c - d) / 2
        cond4 = mflag and abs(b - c) < tolerance_days
        cond5 = (not mflag) and abs(c - d) < tolerance_days
        if cond1 or cond2 or cond3 or cond4 or cond5:
            s = (a + b) / 2
            mflag = True
        else:
            mflag = False
        fs = _f(adapter, s, target_longitude, ayanamsha)
        d, c = c, b
        fc = fb
        if fa * fs < 0:
            b = s
            fb = fs
        else:
            a = s
            fa = fs
        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa
    return b


def solve_solar_ingress(
    target_longitude: float,
    search_start_utc: datetime,
    *,
    adapter: EphemerisAdapter | None = None,
    ayanamsha: str = "lahiri",
) -> SolarIngressSolution:
    adapter = adapter or MoshierAdapter()
    low, high = bracket_crossing(
        target_longitude,
        search_start_utc,
        adapter=adapter,
        ayanamsha=ayanamsha,
    )
    jd = solve_crossing_brent(
        target_longitude,
        low,
        high,
        adapter=adapter,
        ayanamsha=ayanamsha,
    )
    utc_time = jd_ut_to_utc_datetime(jd)
    sign_index = int(target_longitude // 30) % 12
    return SolarIngressSolution(
        target_longitude=target_longitude,
        sign=RASHI_NAMES[sign_index],
        bs_month=sign_index + 1,
        bs_month_name=BS_MONTH_NAMES[sign_index],
        utc_time=utc_time,
        nepal_time=to_nepal_time(utc_time),
        ephemeris=adapter.name,
        ayanamsha=ayanamsha,
    )
