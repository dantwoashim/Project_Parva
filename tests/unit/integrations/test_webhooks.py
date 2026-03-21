from __future__ import annotations

import asyncio
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import app.integrations.webhooks as webhook_module
import pytest
from app.integrations.webhooks import WebhookService


class FakeFestivalRepository:
    def __init__(self, mapping: dict[tuple[str, int], tuple[date, date]]) -> None:
        self.mapping = mapping

    def get_dates(self, festival_id: str, year: int):
        dates = self.mapping.get((festival_id, year))
        if not dates:
            return None
        return SimpleNamespace(start_date=dates[0], end_date=dates[1])


def test_subscription_requires_https_by_default(tmp_path: Path) -> None:
    service = WebhookService(
        db_path=tmp_path / "webhooks.sqlite3",
        legacy_store_path=tmp_path / "legacy.json",
    )

    with pytest.raises(ValueError, match="https://"):
        service.create_subscription(
            subscriber_url="http://example.com/hook",
            festivals=["dashain"],
            remind_days_before=[0],
        )


@pytest.mark.parametrize("url", ["https://127.0.0.1/hook", "https://localhost/hook"])
def test_subscription_rejects_private_targets(tmp_path: Path, url: str) -> None:
    service = WebhookService(
        db_path=tmp_path / "webhooks.sqlite3",
        legacy_store_path=tmp_path / "legacy.json",
    )

    with pytest.raises(ValueError, match="subscriber_url must not"):
        service.create_subscription(
            subscriber_url=url,
            festivals=["dashain"],
            remind_days_before=[0],
        )


def test_dispatch_retries_then_dead_letters_failed_jobs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = WebhookService(
        db_path=tmp_path / "webhooks.sqlite3",
        legacy_store_path=tmp_path / "legacy.json",
        max_attempts=2,
        retry_base_seconds=60,
    )
    service.create_subscription(
        subscriber_url="mock://fail",
        festivals=["dashain"],
        remind_days_before=[0],
    )
    monkeypatch.setattr(
        webhook_module,
        "get_repository",
        lambda: FakeFestivalRepository({("dashain", 2026): (date(2026, 10, 1), date(2026, 10, 1))}),
    )

    first_now = datetime(2026, 10, 1, 6, 0, tzinfo=timezone.utc)
    first = asyncio.run(service.dispatch_for_date(date(2026, 10, 1), now_utc=first_now))
    assert first["queued"] == 1
    assert first["retry_scheduled"] == 1

    queued_jobs = service.list_delivery_jobs(status="retry_scheduled")
    assert len(queued_jobs) == 1
    assert queued_jobs[0]["attestation"]["mode"] == "unsigned"

    second = asyncio.run(service.drain_queue(now_utc=first_now + timedelta(seconds=61)))
    assert second["dead_letter"] == 1

    dead_jobs = service.list_delivery_jobs(status="dead_letter")
    assert len(dead_jobs) == 1
    attempts = service.list_delivery_attempts(dead_jobs[0]["job_id"])
    assert [attempt["status"] for attempt in attempts] == ["retry_scheduled", "dead_letter"]


def test_dispatch_records_hmac_attestation_when_key_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PARVA_WEBHOOK_SIGNING_KEY", "webhook-signing-key")
    monkeypatch.setenv("PARVA_WEBHOOK_SIGNING_KEY_ID", "pytest-webhook-key")

    service = WebhookService(
        db_path=tmp_path / "webhooks.sqlite3",
        legacy_store_path=tmp_path / "legacy.json",
    )
    service.create_subscription(
        subscriber_url="mock://success",
        festivals=["dashain"],
        remind_days_before=[0],
    )
    monkeypatch.setattr(
        webhook_module,
        "get_repository",
        lambda: FakeFestivalRepository({("dashain", 2026): (date(2026, 10, 1), date(2026, 10, 1))}),
    )

    result = asyncio.run(
        service.dispatch_for_date(
            date(2026, 10, 1),
            now_utc=datetime(2026, 10, 1, 6, 0, tzinfo=timezone.utc),
        )
    )
    assert result["sent"] == 1

    job = service.list_delivery_jobs(status="sent")[0]
    assert job["attestation"]["mode"] == "hmac-sha256"
    assert job["attestation"]["key_id"] == "pytest-webhook-key"

    attempts = service.list_delivery_attempts(job["job_id"])
    assert attempts[0]["attestation"]["mode"] == "hmac-sha256"


def test_legacy_json_store_migrates_subscriptions(tmp_path: Path) -> None:
    legacy_path = tmp_path / "subscriptions.json"
    legacy_path.write_text(
        json.dumps(
            {
                "subscriptions": [
                    {
                        "id": "sub_legacy",
                        "subscriber_url": "mock://legacy",
                        "festivals": ["dashain"],
                        "remind_days_before": [0],
                        "format": "json",
                        "active": True,
                        "created_at": "2026-03-20T00:00:00+00:00",
                        "updated_at": "2026-03-20T00:00:00+00:00",
                    }
                ],
                "deliveries": [],
            }
        ),
        encoding="utf-8",
    )

    service = WebhookService(
        db_path=tmp_path / "webhooks.sqlite3",
        legacy_store_path=legacy_path,
    )
    subscriptions = service.list_subscriptions()

    assert len(subscriptions) == 1
    assert subscriptions[0]["id"] == "sub_legacy"
    assert subscriptions[0]["subscriber_url"] == "mock://legacy"
