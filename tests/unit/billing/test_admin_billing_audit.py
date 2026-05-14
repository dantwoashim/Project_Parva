from __future__ import annotations

import json
from types import SimpleNamespace

from app.billing.service import BillingService


def _service() -> BillingService:
    return BillingService(
        SimpleNamespace(
            database_url="sqlite:///:memory:",
            api_key_pepper="test-pepper",
            esewa_merchant_id=None,
            esewa_secret=None,
            esewa_base_url="https://rc.esewa.com.np",
            esewa_return_url=None,
        )
    )


def test_billing_admin_actions_are_persistently_audited_without_secret_key_material():
    service = _service()
    checkout = service.create_checkout(
        email="customer@example.com",
        tier="starter",
        provider="manual_bank_qr",
        name="Sensitive Customer",
    )

    verified = service.verify_checkout(
        checkout["checkout_id"],
        status="paid",
        provider_reference="QR-REF-123456",
        actor_principal="admin",
        route="/v3/api/billing/checkout/id/verify",
        request_id="req-1",
        source_ip="203.0.113.10",
    )
    created = service.create_api_key_for_checkout(
        checkout["checkout_id"],
        actor_principal="admin",
        route="/v3/api/keys",
        request_id="req-2",
    )
    service.revoke_key(
        created["key"]["id"],
        actor_principal="admin",
        route="/v3/api/admin/api-keys/id/revoke",
        request_id="req-3",
    )

    checkout_events = service.audit_events_for_object(
        object_type="checkout",
        object_id=verified["id"],
    )
    key_events = service.audit_events_for_object(
        object_type="api_key",
        object_id=created["key"]["id"],
    )

    assert [event["action"] for event in checkout_events] == ["checkout.verify"]
    assert [event["action"] for event in key_events] == ["api_key.create", "api_key.revoke"]
    assert all(event["before_hash"] or event["after_hash"] for event in checkout_events + key_events)
    assert all(created["api_key"] not in json.dumps(event) for event in checkout_events + key_events)
    assert "QR-REF-123456" not in checkout_events[0]["metadata_json"]


def test_checkout_key_creation_is_idempotent_after_payment_verification():
    service = _service()
    checkout = service.create_checkout(
        email="customer@example.com",
        tier="starter",
        provider="manual_bank_qr",
    )
    service.verify_checkout(checkout["checkout_id"], status="paid")

    first = service.create_api_key_for_checkout(checkout["checkout_id"])
    second = service.create_api_key_for_checkout(checkout["checkout_id"])

    assert first["key"]["id"] == second["key"]["id"]
    assert second["api_key"] is None
