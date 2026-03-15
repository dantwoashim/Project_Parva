"""Settings validation tests."""

import pytest
from app.bootstrap.app_factory import create_app
from app.bootstrap.settings import load_settings


def test_create_app_rejects_webhook_enablement(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PARVA_ENABLE_WEBHOOKS", "true")

    with pytest.raises(RuntimeError, match="Webhook routes are not part of the v3 launch build"):
        create_app()


def test_load_settings_parses_trusted_proxy_ips(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PARVA_TRUSTED_PROXY_IPS", "127.0.0.1, 10.0.0.5")

    settings = load_settings()

    assert settings.trusted_proxy_ips == frozenset({"127.0.0.1", "10.0.0.5"})


def test_load_settings_defaults_to_agpl_license_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PARVA_LICENSE_MODE", raising=False)

    settings = load_settings()

    assert settings.license_mode == "AGPL-3.0-or-later"


def test_create_app_requires_source_url_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PARVA_ENV", "production")
    monkeypatch.delenv("PARVA_SOURCE_URL", raising=False)

    with pytest.raises(RuntimeError, match="PARVA_SOURCE_URL"):
        create_app()
