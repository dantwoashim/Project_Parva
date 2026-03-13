"""Settings validation tests."""

import pytest
from app.bootstrap.app_factory import create_app


def test_create_app_rejects_webhook_enablement(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PARVA_ENABLE_WEBHOOKS", "true")

    with pytest.raises(RuntimeError, match="Webhook routes are not part of the v3 launch build"):
        create_app()
