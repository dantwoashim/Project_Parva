from __future__ import annotations

import pytest
from app.api.billing_routes import VerifyCheckoutRequest, WebhookRequest
from pydantic import ValidationError


def test_verify_checkout_raw_payload_is_bounded() -> None:
    with pytest.raises(ValidationError, match="4096 bytes"):
        VerifyCheckoutRequest(status="paid", raw_payload={"blob": "x" * 5000})


def test_verify_checkout_raw_payload_rejects_deep_nesting() -> None:
    payload = {"a": {"b": {"c": {"d": {"e": {"f": "too deep"}}}}}}

    with pytest.raises(ValidationError, match="nesting depth"):
        VerifyCheckoutRequest(status="paid", raw_payload=payload)


def test_webhook_url_rejects_private_ip_literal() -> None:
    with pytest.raises(ValidationError, match="private"):
        WebhookRequest(url="https://127.0.0.1/hook")


def test_webhook_url_rejects_localhost() -> None:
    with pytest.raises(ValidationError, match="localhost"):
        WebhookRequest(url="https://localhost/hook")


def test_webhook_event_types_are_allowlisted() -> None:
    request = WebhookRequest(url="https://hooks.example.com/parva", event_types=["festival.upcoming"])

    assert request.event_types == ["festival.upcoming"]

    with pytest.raises(ValidationError, match="unsupported webhook event types"):
        WebhookRequest(url="https://hooks.example.com/parva", event_types=["unknown.event"])
