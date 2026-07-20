"""Settings validation tests."""

from dataclasses import replace

import pytest
from app.bootstrap.app_factory import _cors_origins_from_env
from app.bootstrap.settings import load_settings, validate_settings


@pytest.mark.parametrize(
    ("environment", "expected_exposure"),
    [
        ("development", "local"),
        ("test", "local"),
        ("private-service", "private"),
        ("public", "internet"),
        ("staging", "internet"),
        ("production", "internet"),
    ],
)
def test_load_settings_derives_exposure_from_environment(
    monkeypatch: pytest.MonkeyPatch,
    environment: str,
    expected_exposure: str,
) -> None:
    monkeypatch.setenv("PARVA_ENV", environment)
    monkeypatch.delenv("PARVA_EXPOSURE", raising=False)

    settings = load_settings()

    assert settings.exposure == expected_exposure
    assert settings.is_internet_exposed is (expected_exposure == "internet")


def test_public_environment_cannot_downgrade_its_exposure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARVA_ENV", "public")
    monkeypatch.setenv("PARVA_EXPOSURE", "private")

    errors = validate_settings(load_settings())

    assert any("requires PARVA_EXPOSURE=internet" in error for error in errors)


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


@pytest.mark.parametrize(
    ("environment", "explicit_exposure"),
    [
        ("development", "internet"),
        ("test", "internet"),
        ("public", None),
        ("staging", None),
        ("production", None),
    ],
)
def test_internet_exposure_rejects_every_unsafe_deployment_combination(
    monkeypatch: pytest.MonkeyPatch,
    environment: str,
    explicit_exposure: str | None,
) -> None:
    monkeypatch.setenv("PARVA_ENV", environment)
    if explicit_exposure is None:
        monkeypatch.delenv("PARVA_EXPOSURE", raising=False)
    else:
        monkeypatch.setenv("PARVA_EXPOSURE", explicit_exposure)
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "developer_preview")
    monkeypatch.delenv("PARVA_SOURCE_URL", raising=False)
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "memory")
    monkeypatch.delenv("PARVA_SINGLE_PROCESS_RATE_LIMIT", raising=False)
    monkeypatch.setenv("PARVA_DEBUG", "true")
    monkeypatch.setenv("PARVA_TRUSTED_PROXY_IPS", "*")
    monkeypatch.setenv("PARVA_REQUIRE_SIGNED_PROVENANCE_MUTATIONS", "false")
    monkeypatch.setenv("PARVA_REQUIRE_PRECOMPUTED", "false")

    settings = replace(load_settings(), admin_token=None)
    errors = validate_settings(settings)

    assert any("PARVA_SOURCE_URL" in error for error in errors)
    assert any("PARVA_DEBUG=true" in error for error in errors)
    assert any("PARVA_ADMIN_TOKEN" in error for error in errors)
    assert any("PARVA_TRUSTED_PROXY_IPS=*" in error for error in errors)
    assert any("PARVA_RATE_LIMIT_BACKEND=redis" in error for error in errors)
    assert any("PARVA_REQUIRE_SIGNED_PROVENANCE_MUTATIONS=false" in error for error in errors)


def test_public_demo_can_explicitly_accept_one_process_rate_limiting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARVA_ENV", "public")
    monkeypatch.setenv("PARVA_EXPOSURE", "internet")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_reference")
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "memory")
    monkeypatch.setenv("PARVA_SINGLE_PROCESS_RATE_LIMIT", "true")
    monkeypatch.setenv("PARVA_REQUIRE_PRECOMPUTED", "false")
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY", "test-provenance-key")

    settings = load_settings()

    assert settings.environment == "public"
    assert settings.exposure == "internet"
    assert settings.require_precomputed is False
    assert validate_settings(settings) == []


def test_public_environment_rejects_localhost_cors_origins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.bootstrap.app_factory import create_app

    monkeypatch.setenv("PARVA_ENV", "public")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_reference")
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "memory")
    monkeypatch.setenv("PARVA_SINGLE_PROCESS_RATE_LIMIT", "true")
    monkeypatch.setenv("PARVA_REQUIRE_PRECOMPUTED", "false")
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY", "test-provenance-key")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://localhost:5173")

    with pytest.raises(RuntimeError, match="internet-exposed CORS origins cannot include localhost"):
        create_app()


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

    with pytest.raises(RuntimeError, match="Internet-exposed.*PARVA_SOURCE_URL"):
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

    with pytest.raises(RuntimeError, match="Internet-exposed.*PARVA_RATE_LIMIT_BACKEND=redis"):
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
