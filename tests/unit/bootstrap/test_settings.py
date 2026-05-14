"""Settings validation tests."""

import pytest
from app.bootstrap.app_factory import _cors_origins_from_env
from app.bootstrap.settings import load_settings, validate_settings


def test_load_settings_parses_trusted_proxy_ips(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PARVA_TRUSTED_PROXY_IPS", "127.0.0.1, 10.0.0.5")

    settings = load_settings()

    assert settings.trusted_proxy_ips == frozenset({"127.0.0.1", "10.0.0.5"})


def test_production_rejects_wildcard_trusted_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("PARVA_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("PARVA_TRUSTED_PROXY_IPS", "*")

    settings = load_settings()

    assert any("PARVA_TRUSTED_PROXY_IPS=*" in error for error in validate_settings(settings))


def test_staging_rejects_wildcard_trusted_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PARVA_ENV", "staging")
    monkeypatch.setenv("PARVA_TRUSTED_PROXY_IPS", "*")

    settings = load_settings()

    assert any("PARVA_TRUSTED_PROXY_IPS=*" in error for error in validate_settings(settings))


def test_load_settings_defaults_to_agpl_license_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PARVA_LICENSE_MODE", raising=False)

    settings = load_settings()

    assert settings.license_mode == "AGPL-3.0-or-later"


def test_load_settings_exposes_test_only_credentials_under_pytest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PARVA_ADMIN_TOKEN", raising=False)
    monkeypatch.delenv("PARVA_API_KEYS", raising=False)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/unit/bootstrap/test_settings.py::test")

    settings = load_settings()

    assert settings.admin_token == "parva-test-admin-token"
    assert settings.api_keys["local-read"].secret == "parva-test-read-key"


def test_load_settings_requires_precomputed_by_default_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.delenv("PARVA_REQUIRE_PRECOMPUTED", raising=False)

    settings = load_settings()

    assert settings.require_precomputed is True
    assert settings.prewarm_hotset is True


def test_load_settings_allows_explicit_precomputed_override_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.setenv("PARVA_REQUIRE_PRECOMPUTED", "false")

    settings = load_settings()

    assert settings.require_precomputed is False


def test_public_render_profile_allows_memory_rate_limiter_without_source_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARVA_ENV", "public")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "developer_preview")
    monkeypatch.delenv("PARVA_SOURCE_URL", raising=False)
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "memory")
    monkeypatch.setenv("PARVA_REQUIRE_PRECOMPUTED", "false")

    settings = load_settings()

    assert settings.environment == "public"
    assert settings.require_precomputed is False
    assert validate_settings(settings) == []


def test_cors_origins_accept_parva_prefixed_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CORS_ALLOW_ORIGINS", raising=False)
    monkeypatch.setenv(
        "PARVA_CORS_ORIGINS",
        "https://prabinghimire1.com.np, https://project-parva.pages.dev",
    )

    assert _cors_origins_from_env() == [
        "https://prabinghimire1.com.np",
        "https://project-parva.pages.dev",
    ]


def test_create_app_requires_source_url_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.bootstrap.app_factory import create_app

    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_reference")
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("PARVA_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("PARVA_REQUIRE_PRECOMPUTED", "false")
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY", "test-provenance-key")
    monkeypatch.delenv("PARVA_SOURCE_URL", raising=False)

    with pytest.raises(RuntimeError, match="PARVA_SOURCE_URL.*PARVA_ENV=public"):
        create_app()


def test_create_app_requires_distributed_rate_limiting_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.bootstrap.app_factory import create_app

    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_reference")
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "memory")
    monkeypatch.setenv("PARVA_REQUIRE_PRECOMPUTED", "false")
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY", "test-provenance-key")

    with pytest.raises(RuntimeError, match="PARVA_RATE_LIMIT_BACKEND=redis.*PARVA_ENV=public"):
        create_app()


def test_create_app_requires_precomputed_artifacts_in_production_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.bootstrap.app_factory as app_factory

    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_reference")
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("PARVA_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY", "test-provenance-key")
    monkeypatch.delenv("PARVA_REQUIRE_PRECOMPUTED", raising=False)
    monkeypatch.setattr(
        app_factory,
        "get_cache_stats",
        lambda: {"file_count": 0, "total_bytes": 0, "files": [], "freshness": {}},
    )

    with pytest.raises(RuntimeError, match="requires precomputed artifacts"):
        app_factory.create_app()
