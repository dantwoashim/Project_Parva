"""Shared BS year mapping helpers."""

from __future__ import annotations


def bs_solar_year_for_gregorian_year(gregorian_year: int, bs_month: int) -> int:
    """Map a Gregorian year to the BS solar year for a given BS month.

    BS months 10-12 (Magh, Falgun, Chaitra) usually fall in Jan-Mar of the
    Gregorian year, while BS months 1-9 align with Apr-Dec and therefore map
    to the Gregorian year + 57.
    """

    return gregorian_year + (56 if int(bs_month) >= 10 else 57)


__all__ = ["bs_solar_year_for_gregorian_year"]
