from __future__ import annotations

from dataclasses import replace

from app.bootstrap.settings import load_settings, validate_settings


def _production_safe_defaults(monkeypatch):
    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_reference")
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("PARVA_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("PARVA_REQUIRE_PRECOMPUTED", "false")
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY", "test-provenance-key")


def _errors(monkeypatch) -> list[str]:
    return validate_settings(load_settings())


def test_production_rejects_debug_mode(monkeypatch):
    _production_safe_defaults(monkeypatch)
    monkeypatch.setenv("PARVA_DEBUG", "true")

    assert any("PARVA_DEBUG=true" in error for error in _errors(monkeypatch))


def test_staging_rejects_memory_rate_limiter(monkeypatch):
    _production_safe_defaults(monkeypatch)
    monkeypatch.setenv("PARVA_ENV", "staging")
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "memory")

    assert any("PARVA_RATE_LIMIT_BACKEND=redis" in error for error in _errors(monkeypatch))


def test_production_rejects_private_route_profiles(monkeypatch):
    _production_safe_defaults(monkeypatch)
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "research_private")

    assert any("cannot use research_private" in error for error in _errors(monkeypatch))


def test_public_profile_rejects_full_private_surface(monkeypatch):
    monkeypatch.setenv("PARVA_ENV", "public")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "full_dev")

    assert any("cannot use research_private" in error for error in _errors(monkeypatch))


def test_deployed_provenance_mutations_must_be_signed(monkeypatch):
    _production_safe_defaults(monkeypatch)
    monkeypatch.delenv("PARVA_PROVENANCE_ATTESTATION_KEY", raising=False)
    monkeypatch.setenv("PARVA_REQUIRE_SIGNED_PROVENANCE_MUTATIONS", "false")

    errors = _errors(monkeypatch)

    assert any("PARVA_REQUIRE_SIGNED_PROVENANCE_MUTATIONS=false" in error for error in errors)


def test_deployed_provenance_requires_attestation_key(monkeypatch):
    _production_safe_defaults(monkeypatch)
    monkeypatch.delenv("PARVA_PROVENANCE_ATTESTATION_KEY", raising=False)
    monkeypatch.delenv("PARVA_PROVENANCE_ATTESTATION_KEY_FILE", raising=False)

    assert any("PARVA_PROVENANCE_ATTESTATION_KEY" in error for error in _errors(monkeypatch))


def test_production_billing_requires_admin_postgres_and_nondefault_pepper(monkeypatch):
    _production_safe_defaults(monkeypatch)
    monkeypatch.setenv("PARVA_BILLING_ENABLED", "true")
    monkeypatch.setenv("PARVA_DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("PARVA_API_KEY_PEPPER", "parva-local-development-pepper")

    settings = replace(load_settings(), admin_token=None)
    errors = validate_settings(settings)

    assert any("PARVA_ADMIN_TOKEN" in error for error in errors)
    assert any("Postgres PARVA_DATABASE_URL" in error for error in errors)
    assert any("PARVA_API_KEY_PEPPER" in error for error in errors)
