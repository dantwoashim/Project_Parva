"""MCP stdio server: the API's answers as tools.  `pip install parva-calendar[mcp]`, then `parva-mcp`."""

from __future__ import annotations

from datetime import date
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import api
from .astro import KATHMANDU

server = FastMCP("parva")


def convert(ad: str | None = None, bs: str | None = None) -> dict[str, Any]:
    """Convert a date: pass ad=2026-04-14 or bs=2083-01-01."""
    return api.convert(ad=date.fromisoformat(ad) if ad else None, bs_date=bs)


def working_day(ad: str) -> dict[str, Any]:
    """Is this AD date a working day in Nepal?"""
    return api.working_day(ad=date.fromisoformat(ad))


def holidays(bs_year: int, scope: str = "national") -> dict[str, Any]:
    """Gazetted public holidays for a BS year."""
    return api.year_holidays(bs_year=bs_year, scope=scope)


def festival(id: str, year: int) -> dict[str, Any]:
    """One festival's date, source and mythology for a Gregorian year."""
    return api.festival(fid=id, year=year)


def festivals(year: int) -> dict[str, Any]:
    """Every festival with a date in a Gregorian year."""
    return api.list_festivals(year=year)


def panchanga(
    ad: str, lat: float = KATHMANDU[1], lon: float = KATHMANDU[0], tz: str = "Asia/Kathmandu"
) -> dict[str, Any]:
    """Tithi, paksha, nakshatra, yoga, karana at sunrise."""
    return api.panchanga(ad=date.fromisoformat(ad), lat=lat, lon=lon, tz=tz)


def audit(year: int) -> dict[str, Any]:
    """Where the Ministry of Home Affairs and the astronomy disagree."""
    return api.audit(year=year)


for _fn in (convert, working_day, holidays, festival, festivals, panchanga, audit):
    server.add_tool(_fn)


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
