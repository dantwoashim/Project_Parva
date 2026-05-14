from __future__ import annotations

import json
import logging

from app.billing import reset_billing_service_cache
from app.bootstrap.app_factory import create_app
from fastapi.testclient import TestClient


def _client(monkeypatch):
    reset_billing_service_cache()
    monkeypatch.setenv("PARVA_BILLING_ENABLED", "true")
    monkeypatch.setenv("PARVA_DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("PARVA_API_KEY_PEPPER", "test-pepper")
    return TestClient(create_app())


def test_billing_checkout_activation_and_api_key_usage(monkeypatch, caplog):
    caplog.set_level(logging.INFO, logger="parva.billing.audit")
    client = _client(monkeypatch)

    checkout_response = client.post(
        "/v3/api/billing/checkout",
        json={
            "email": "customer@example.com",
            "name": "Customer",
            "tier": "starter",
            "provider": "manual_bank_qr",
        },
    )
    assert checkout_response.status_code == 200
    checkout_id = checkout_response.json()["checkout_id"]

    invalid = client.get("/v3/api/calendar/today", headers={"X-API-Key": "bad-key"})
    assert invalid.status_code == 401

    checkout_payload = checkout_response.json()
    assert checkout_payload["status"] == "manual_invoice"
    assert checkout_payload["provider"] == "manual_bank_qr"

    verify_response = client.post(
        f"/v3/api/admin/invoices/{checkout_payload['invoice_id']}/mark-paid",
        headers={"Authorization": "Bearer parva-test-admin-token"},
        json={"provider_reference": "manual-qr-paid", "notes": "QR payment screenshot received."},
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["status"] == "paid"
    audit_entries = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "parva.billing.audit"
    ]

    def _invoice_id_matches_logged_value(logged_invoice_id: str | None) -> bool:
        if logged_invoice_id == checkout_payload["invoice_id"]:
            return True
        if not isinstance(logged_invoice_id, str) or "[redacted]" not in logged_invoice_id:
            return False
        visible_prefix = logged_invoice_id.split("[redacted]", 1)[0]
        return checkout_payload["invoice_id"].startswith(visible_prefix)

    assert any(
        entry["action_type"] == "invoice.mark_paid"
        and _invoice_id_matches_logged_value(entry.get("invoice_id"))
        and entry["provider_reference"] == "[redacted]"
        for entry in audit_entries
    )

    key_response = client.post("/v3/api/keys", json={"checkout_id": checkout_id})
    assert key_response.status_code == 200
    api_key = key_response.json()["api_key"]
    assert api_key.startswith("parva_live_")

    usage_response = client.get("/v3/api/me/usage", headers={"X-API-Key": api_key})
    assert usage_response.status_code == 200
    usage = usage_response.json()
    assert usage["tier"] == "starter"
    assert usage["limit"] == 5000


def test_payoneer_manual_invoice_requires_admin_confirmation(monkeypatch):
    client = _client(monkeypatch)

    checkout_response = client.post(
        "/v3/api/billing/checkout",
        json={
            "email": "international@example.com",
            "tier": "professional",
            "provider": "payoneer",
        },
    )
    assert checkout_response.status_code == 200
    payload = checkout_response.json()
    assert payload["status"] == "manual_invoice"

    key_response = client.post("/v3/api/keys", json={"checkout_id": payload["checkout_id"]})
    assert key_response.status_code == 403

    paid_response = client.post(
        f"/v3/api/admin/invoices/{payload['invoice_id']}/mark-paid",
        headers={"Authorization": "Bearer parva-test-admin-token"},
        json={"provider_reference": "payoneer-confirmed", "notes": "Manual invoice cleared."},
    )
    assert paid_response.status_code == 200
    assert paid_response.json()["status"] == "paid"

    activated_key = client.post("/v3/api/keys", json={"checkout_id": payload["checkout_id"]})
    assert activated_key.status_code == 200
    assert activated_key.json()["api_key"].startswith("parva_live_")


def test_production_checkout_verify_does_not_trust_client_status(monkeypatch):
    reset_billing_service_cache()
    monkeypatch.setenv("PARVA_BILLING_ENABLED", "true")
    monkeypatch.setenv("PARVA_DATABASE_URL", "postgresql://example.invalid/parva")
    monkeypatch.setenv("PARVA_API_KEY_PEPPER", "prod-pepper")
    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("PARVA_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("PARVA_REQUIRE_PRECOMPUTED", "false")

    from app.api.billing_routes import VerifyCheckoutRequest, verify_billing_checkout

    # The route must reject non-admin production activation before it ever
    # touches a provider payload or database state.
    class _State:
        settings = create_app.__globals__["load_settings"]()

    class _Request:
        app = type("App", (), {"state": _State()})()
        state = type("RequestState", (), {"principal": None})()

    import pytest
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        import anyio

        anyio.run(
            verify_billing_checkout,
            "pay_fake",
            VerifyCheckoutRequest(status="Completed"),
            _Request(),
        )
    assert exc.value.status_code == 403
