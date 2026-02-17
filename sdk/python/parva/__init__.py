"""
Parva Python SDK
=================

Client library for the Parva API — Nepal's temporal infrastructure.

Usage:
    from parva import ParvaClient

    client = ParvaClient("https://parva.example.com")

    # Convert date
    result = client.convert("2026-02-16")

    # Get today's panchanga
    panchanga = client.panchanga("2026-02-16")

    # Cross-calendar conversion
    islamic = client.cross_convert("2026-02-16", "islamic")

    # Download iCal feed
    ics = client.ical(year=2082)
"""

import json
from typing import Optional, Dict, Any, List
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode


class ParvaError(Exception):
    """Error from Parva API."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Parva API error {status_code}: {detail}")


class ParvaClient:
    """
    Python client for the Parva Festival Discovery API.

    Args:
        base_url: Parva API base URL (no trailing slash)
        timeout: Request timeout in seconds
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to API."""
        url = f"{self.base_url}{path}"
        if params:
            url += "?" + urlencode(params)
        req = Request(url, headers={"Accept": "application/json"})
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            body = e.read().decode()
            try:
                detail = json.loads(body).get("detail", body)
            except (json.JSONDecodeError, KeyError):
                detail = body
            raise ParvaError(e.code, detail)

    def _get_raw(self, path: str, params: Optional[Dict] = None) -> str:
        """Make GET request and return raw text."""
        url = f"{self.base_url}{path}"
        if params:
            url += "?" + urlencode(params)
        req = Request(url)
        with urlopen(req, timeout=self.timeout) as resp:
            return resp.read().decode()

    # ── Core Calendar ───────────────────────────────────────────────
    def convert(self, date: str) -> Dict:
        """Convert Gregorian date to BS, NS, and get tithi."""
        return self._get("/api/calendar/convert", {"date": date})

    def today(self) -> Dict:
        """Get today's calendar info."""
        return self._get("/api/calendar/today")

    def panchanga(self, date: str) -> Dict:
        """Get full panchanga for a date."""
        return self._get("/api/calendar/panchanga", {"date": date})

    def panchanga_range(self, start: str, days: int = 7) -> Dict:
        """Get panchanga for a range of dates."""
        return self._get("/api/calendar/panchanga/range", {"start": start, "days": days})

    # ── Festivals ───────────────────────────────────────────────────
    def calculate_festival(self, festival_id: str, year: int) -> Dict:
        """Calculate dates for a specific festival."""
        return self._get(f"/api/calendar/festivals/calculate/{festival_id}", {"year": year})

    def upcoming_festivals(self, days: int = 30) -> Dict:
        """Get upcoming festivals."""
        return self._get("/api/calendar/festivals/upcoming", {"days": days})

    # ── Cross-Calendar ──────────────────────────────────────────────
    def cross_convert(self, date: str, to: str) -> Dict:
        """Convert Gregorian date to another calendar system."""
        return self._get("/api/calendar/cross/convert", {"date": date, "to": to})

    def convert_all(self, date: str) -> Dict:
        """Convert date to all registered calendar systems."""
        return self._get("/api/calendar/cross/convert-all", {"date": date})

    def calendars(self) -> Dict:
        """List available calendar systems."""
        return self._get("/api/calendar/cross/calendars")

    # ── iCal ────────────────────────────────────────────────────────
    def ical(self, year: Optional[int] = None) -> str:
        """Download iCal feed as .ics string."""
        params = {"year": year} if year else {}
        return self._get_raw("/api/calendar/ical", params)

    # ── Engine ──────────────────────────────────────────────────────
    def health(self) -> Dict:
        """Check engine health."""
        return self._get("/api/engine/health")

    def engine_config(self) -> Dict:
        """Get engine configuration."""
        return self._get("/api/engine/config")
