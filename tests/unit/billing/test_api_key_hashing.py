from __future__ import annotations

from app.billing.keys import (
    hash_api_key_secret,
    verify_api_key_secret,
)
from app.bootstrap.settings import load_settings, validate_settings


def test_api_key_hash_uses_salted_versioned_pbkdf2():
    secret = "sample-secret"
    pepper = "sample-pepper"

    first = hash_api_key_secret(secret, pepper)
    second = hash_api_key_secret(secret, pepper)

    assert first.startswith("pbkdf2_sha256$")
    assert second.startswith("pbkdf2_sha256$")
    assert first != second
    assert verify_api_key_secret(secret, pepper, first) is True
    assert verify_api_key_secret("wrong-secret", pepper, first) is False


def test_api_key_hash_verifier_keeps_legacy_sha256_compatibility():
    legacy = "37ed63206cdbaf3f6675549dadf40ba61f411d59ec57ec7c12e439a317d5d39b"

    assert verify_api_key_secret("secret", "pepper", legacy) is True
    assert verify_api_key_secret("secret", "wrong-pepper", legacy) is False


def test_default_api_key_pepper_fails_when_public_billing_enabled(monkeypatch):
    monkeypatch.setenv("PARVA_ENV", "public")
    monkeypatch.setenv("PARVA_BILLING_ENABLED", "true")
    monkeypatch.setenv("PARVA_DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.delenv("PARVA_API_KEY_PEPPER", raising=False)

    errors = validate_settings(load_settings())

    assert any("PARVA_API_KEY_PEPPER" in error for error in errors)
