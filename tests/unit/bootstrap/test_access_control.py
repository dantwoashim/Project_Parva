from __future__ import annotations

import pytest
from app.bootstrap.access_control import classify_request, find_unclassified_api_routes
from fastapi import FastAPI


def test_classify_request_keeps_calendar_routes_public():
    requirement = classify_request("/v3/api/calendar/today", "GET")

    assert requirement.required is False
    assert requirement.policy_name == "public"


def test_classify_request_defaults_unknown_api_routes_to_denied():
    requirement = classify_request("/v3/api/unlisted-surface", "GET")

    assert requirement.required is True
    assert requirement.policy_name == "unclassified_api"
    assert requirement.admin_only is True


def test_billing_route_policies_are_explicit():
    cases = {
        ("GET", "/v3/api/billing/plans"): (False, "billing_plans_public"),
        ("POST", "/v3/api/billing/checkout"): (False, "billing_checkout_create_public"),
        ("GET", "/v3/api/billing/checkout/pay_123"): (False, "billing_checkout_status_public"),
        ("POST", "/v3/api/billing/checkout/pay_123/verify"): (
            False,
            "billing_checkout_verify_public_or_admin",
        ),
        ("POST", "/v3/api/keys"): (False, "billing_key_claim_public"),
        ("DELETE", "/v3/api/keys/key_123"): (True, "billing_key_revoke"),
        ("GET", "/v3/api/me/usage"): (False, "billing_usage_public_or_key"),
        ("POST", "/v3/api/webhooks"): (True, "billing_webhook_create"),
    }

    for (method, path), (required, policy_name) in cases.items():
        requirement = classify_request(path, method)
        assert requirement.required is required
        assert requirement.policy_name == policy_name


def test_unknown_billing_subroutes_require_admin():
    requirement = classify_request("/v3/api/billing/internal-surprise", "POST")

    assert requirement.required is True
    assert requirement.policy_name == "billing_unclassified_admin"
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
