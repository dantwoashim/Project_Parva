from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import app.api.forecast_routes as forecast_routes
import app.calendar.routes as calendar_routes
import pytest
from app.bootstrap.app_factory import create_app
from app.core.clock import FixedClock
from fastapi.testclient import TestClient


def _date_echo(**kwargs):
    return {
        "gregorian": kwargs["today"].isoformat(),
        "timezone": kwargs["timezone_name"],
    }


def test_today_endpoint_tracks_kathmandu_midnight_without_restart(monkeypatch) -> None:
    monkeypatch.setattr(calendar_routes, "build_today_payload", _date_echo)
    app = create_app()
    client = TestClient(app)

    app.state.clock = FixedClock(datetime(2026, 7, 15, 18, 14, tzinfo=timezone.utc))
    assert client.get("/api/calendar/today").json()["gregorian"] == "2026-07-15"

    app.state.clock = FixedClock(datetime(2026, 7, 15, 18, 15, tzinfo=timezone.utc))
    payload = client.get("/api/calendar/today").json()
    assert payload == {"gregorian": "2026-07-16", "timezone": "Asia/Kathmandu"}


def test_today_endpoint_honors_requested_timezone(monkeypatch) -> None:
    monkeypatch.setattr(calendar_routes, "build_today_payload", _date_echo)
    app = create_app()
    app.state.clock = FixedClock(datetime(2026, 7, 15, 18, 15, tzinfo=timezone.utc))
    client = TestClient(app)

    payload = client.get("/api/calendar/today", params={"tz": "America/New_York"}).json()

    assert payload == {"gregorian": "2026-07-15", "timezone": "America/New_York"}
    assert client.get("/api/calendar/today", params={"tz": "Mars/Olympus"}).status_code == 422


def test_public_demo_panchanga_default_uses_the_same_clock(monkeypatch) -> None:
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_demo")
    monkeypatch.setenv("PARVA_ENV", "test")

    def panchanga_echo(target_date, **kwargs):
        return {"date": target_date.isoformat(), "timezone": kwargs["timezone_name"]}

    monkeypatch.setattr(
        "app.services.calendar_surface_service.build_panchanga_payload",
        panchanga_echo,
    )
    app = create_app()
    app.state.clock = FixedClock(datetime(2026, 7, 15, 18, 15, tzinfo=timezone.utc))
    client = TestClient(app)

    payload = client.get("/v3/api/calendar/panchanga").json()

    assert payload == {"date": "2026-07-16", "timezone": "Asia/Kathmandu"}


def test_forecast_default_year_changes_at_new_year_without_restart(monkeypatch) -> None:
    monkeypatch.setattr(
        forecast_routes,
        "build_error_curve",
        lambda start, end: [{"year": start}, {"year": end}],
    )
    app = create_app()
    client = TestClient(app)

    app.state.clock = FixedClock(datetime(2030, 12, 31, 18, 14, tzinfo=timezone.utc))
    before = client.get("/api/forecast/error-curve").json()
    app.state.clock = FixedClock(datetime(2030, 12, 31, 18, 15, tzinfo=timezone.utc))
    after = client.get("/api/forecast/error-curve").json()

    assert (before["start_year"], before["end_year"]) == (2030, 2055)
    assert (after["start_year"], after["end_year"]) == (2031, 2056)


@pytest.mark.parametrize(
    "relative_path",
    [
        "backend/app/services/calendar_surface_service.py",
        "backend/app/services/agent_service.py",
        "backend/app/services/compliance_service.py",
        "backend/app/api/public_demo_routes.py",
        "backend/app/calendar/routes.py",
        "backend/app/api/forecast_routes.py",
    ],
)
def test_calendar_request_modules_do_not_read_the_host_clock(relative_path: str) -> None:
    project_root = Path(__file__).resolve().parents[2]
    source = (project_root / relative_path).read_text(encoding="utf-8")

    assert "date.today(" not in source
    assert "datetime.now(" not in source
