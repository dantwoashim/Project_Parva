"""Default engine implementation backed by current calendar modules."""

from __future__ import annotations

from datetime import date, datetime

from app.calendar import (
    bs_to_gregorian,
    calculate_tithi,
    get_bs_month_name,
    gregorian_to_bs,
)
from app.calendar.bikram_sambat import get_bs_confidence
from app.calendar.tithi import get_moon_phase_name
from app.calendar.panchanga import get_panchanga

from .interface import EngineInterface
from .time_utils import ensure_utc
from .types import ConversionResult, EngineMeta, PanchangaResult, TithiResult


class ParvaEngine(EngineInterface):
    """V2 computation engine adapter."""

    def calculate_tithi(self, dt: date | datetime) -> TithiResult:
        utc_dt = ensure_utc(dt)
        data = calculate_tithi(utc_dt)
        return TithiResult(
            number=int(data["number"]),
            display_number=int(data["display_number"]),
            paksha=data["paksha"],
            name=data["name"],
            moon_phase=get_moon_phase_name(utc_dt),
            meta=EngineMeta(method="ephemeris", confidence="computed", source="swiss_moshier"),
        )

    def calculate_panchanga(self, dt: date | datetime) -> PanchangaResult:
        utc_dt = ensure_utc(dt)
        data = get_panchanga(utc_dt.date())
        return PanchangaResult(
            date=utc_dt.date(),
            tithi=data["tithi"],
            nakshatra=data["nakshatra"],
            yoga=data["yoga"],
            karana=data["karana"],
            vaara=data["vaara"],
            meta=EngineMeta(method="ephemeris", confidence="astronomical", source=data.get("mode", "swiss_moshier")),
        )

    def convert_date(self, from_calendar: str, to_calendar: str, value: str) -> ConversionResult:
        if from_calendar == "gregorian" and to_calendar == "bs":
            y, m, d = [int(v) for v in value.split("-")]
            gdate = date(y, m, d)
            bsy, bsm, bsd = gregorian_to_bs(gdate)
            confidence = get_bs_confidence(gdate)
            return ConversionResult(
                from_calendar="gregorian",
                to_calendar="bs",
                input_date=value,
                output_date=f"{bsy:04d}-{bsm:02d}-{bsd:02d}",
                source_range="official table" if confidence == "official" else "estimated model",
                meta=EngineMeta(method="lookup", confidence=confidence, source=get_bs_month_name(bsm)),
            )

        if from_calendar == "bs" and to_calendar == "gregorian":
            y, m, d = [int(v) for v in value.split("-")]
            gdate = bs_to_gregorian(y, m, d)
            confidence = "official" if 2000 <= y <= 2090 else "estimated"
            return ConversionResult(
                from_calendar="bs",
                to_calendar="gregorian",
                input_date=value,
                output_date=gdate.isoformat(),
                source_range="BS 2000-2090 table" if confidence == "official" else "extended estimator",
                meta=EngineMeta(method="lookup", confidence=confidence, source="bs_month_lengths"),
            )

        raise ValueError(f"Unsupported conversion: {from_calendar} -> {to_calendar}")


def get_default_engine() -> ParvaEngine:
    """Factory for default computation engine."""
    return ParvaEngine()
