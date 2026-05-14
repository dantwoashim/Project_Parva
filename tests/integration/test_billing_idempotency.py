from __future__ import annotations

from app.billing import reset_billing_service_cache
from app.bootstrap.app_factory import create_app
from fastapi.testclient import TestClient


def _client(monkeypatch):
    reset_billing_service_cache()
    monkeypatch.setenv("PARVA_BILLING_ENABLED", "true")
    monkeypatch.setenv("PARVA_DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("PARVA_API_KEY_PEPPER", "test-pepper")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    return TestClient(create_app())


def test_manual_payment_activation_and_key_creation_are_idempotent(monkeypatch):
    client = _client(monkeypatch)
    checkout_response = client.post(
        "/v3/api/billing/checkout",
        json={
            "email": "customer@example.com",
            "tier": "starter",
            "provider": "manual_bank_qr",
        },
    )
    assert checkout_response.status_code == 200
    checkout = checkout_response.json()

    first_paid = client.post(
        f"/v3/api/admin/invoices/{checkout['invoice_id']}/mark-paid",
        headers={"Authorization": "Bearer parva-test-admin-token"},
        json={"provider_reference": "same-ref"},
    )
    second_paid = client.post(
        f"/v3/api/admin/invoices/{checkout['invoice_id']}/mark-paid",
        headers={"Authorization": "Bearer parva-test-admin-token"},
        json={"provider_reference": "same-ref"},
    )

    assert first_paid.status_code == 200
    assert second_paid.status_code == 200
    assert first_paid.json()["status"] == "paid"
    assert second_paid.json()["status"] == "paid"

    first_key = client.post("/v3/api/keys", json={"checkout_id": checkout["checkout_id"]})
    second_key = client.post("/v3/api/keys", json={"checkout_id": checkout["checkout_id"]})

    assert first_key.status_code == 200
    assert second_key.status_code == 200
    assert first_key.json()["api_key"].startswith("parva_live_")
    assert second_key.json()["api_key"] is None
    assert first_key.json()["key"]["id"] == second_key.json()["key"]["id"]
