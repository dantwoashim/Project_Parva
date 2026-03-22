"""Settings validation tests."""

import pytest
from app.bootstrap.settings import load_settings


def test_load_settings_parses_trusted_proxy_ips(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PARVA_TRUSTED_PROXY_IPS", "127.0.0.1, 10.0.0.5")

    settings = load_settings()

    assert settings.trusted_proxy_ips == frozenset({"127.0.0.1", "10.0.0.5"})


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


def test_create_app_requires_source_url_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.bootstrap.app_factory import create_app

    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.delenv("PARVA_SOURCE_URL", raising=False)

    with pytest.raises(RuntimeError, match="PARVA_SOURCE_URL"):
        create_app()


def test_create_app_requires_distributed_rate_limiting_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.bootstrap.app_factory import create_app

    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://example.com/source")
    monkeypatch.setenv("PARVA_RATE_LIMIT_BACKEND", "memory")

    with pytest.raises(RuntimeError, match="PARVA_RATE_LIMIT_BACKEND=redis"):
        create_app()
