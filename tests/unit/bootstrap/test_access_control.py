from __future__ import annotations

import pytest
from fastapi import FastAPI

from app.bootstrap.access_control import classify_request, find_unclassified_api_routes


def test_classify_request_keeps_calendar_routes_public():
    requirement = classify_request("/v3/api/calendar/today", "GET")

    assert requirement.required is False
    assert requirement.policy_name == "public"


def test_classify_request_defaults_unknown_api_routes_to_denied():
    requirement = classify_request("/v3/api/unlisted-surface", "GET")

    assert requirement.required is True
    assert requirement.policy_name == "unclassified_api"
    assert requirement.admin_only is True


def test_classify_request_respects_segment_boundaries_for_public_artifacts_prefix():
    requirement = classify_request("/v3/api/public-artifacts/manifest", "GET")

    assert requirement.required is True
    assert requirement.policy_name == "unclassified_api"
    assert requirement.admin_only is True


def test_find_unclassified_api_routes_reports_missing_policies():
    app = FastAPI()

    @app.get("/api/demo")
    async def demo():
        return {"ok": True}

    missing = find_unclassified_api_routes(app.routes)

    assert "GET /api/demo" in missing


def test_create_app_fails_if_registered_api_routes_are_unclassified(monkeypatch: pytest.MonkeyPatch):
    import app.bootstrap.app_factory as app_factory

    original_register = app_factory.register_routers

    def register_with_gap(*args, **kwargs):
        original_register(*args, **kwargs)

        app = args[0]

        @app.get("/api/demo")
        async def demo():
            return {"ok": True}

    monkeypatch.setattr(app_factory, "register_routers", register_with_gap)

    with pytest.raises(RuntimeError, match="unclassified API routes"):
        app_factory.create_app()
