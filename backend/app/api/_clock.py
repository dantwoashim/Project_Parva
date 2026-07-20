"""FastAPI adapters for the canonical application clock."""

from __future__ import annotations

from datetime import date

from fastapi import HTTPException, Request

from app.core.clock import DEFAULT_CIVIL_TIMEZONE, SYSTEM_CLOCK, Clock, civil_date


def request_clock(request: Request) -> Clock:
    """Return the app-scoped clock, with a production-safe fallback."""

    return getattr(request.app.state, "clock", SYSTEM_CLOCK)


def request_civil_date(
    request: Request,
    timezone_name: str = DEFAULT_CIVIL_TIMEZONE,
) -> date:
    """Resolve the request's current date without consulting the host timezone."""

    try:
        return civil_date(clock=request_clock(request), timezone_name=timezone_name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


__all__ = ["request_civil_date", "request_clock"]
