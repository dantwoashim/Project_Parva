"""Webhook subscription service with durable queue-backed delivery."""

from __future__ import annotations

import asyncio
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

try:  # Optional runtime dependency in constrained environments.
    import aiohttp
except Exception:  # pragma: no cover
    aiohttp = None

from app.festivals.repository import get_repository
from app.integrations.webhook_store import (
    DB_PATH,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_RETRY_BASE_SECONDS,
    LEGACY_STORE_PATH,
    WebhookDeliveryQueue,
    WebhookStore,
    WebhookSubscriptionRepository,
    build_webhook_attestation,
    delivery_headers,
    utc_now,
)


class WebhookService:
    """Durable webhook subscription service with queued delivery semantics."""

    def __init__(
        self,
        db_path: Path | None = None,
        *,
        legacy_store_path: Path | None = None,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        retry_base_seconds: int = DEFAULT_RETRY_BASE_SECONDS,
    ) -> None:
        self.store = WebhookStore(
            db_path=db_path or DB_PATH,
            legacy_store_path=legacy_store_path or LEGACY_STORE_PATH,
        )
        self.repository = WebhookSubscriptionRepository(self.store)
        self.queue = WebhookDeliveryQueue(
            self.store,
            max_attempts=max_attempts,
            retry_base_seconds=retry_base_seconds,
        )

    def list_subscriptions(self) -> list[dict[str, Any]]:
        return self.repository.list_subscriptions()

    def create_subscription(
        self,
        *,
        subscriber_url: str,
        festivals: list[str],
        remind_days_before: list[int],
        payload_format: str = "json",
        active: bool = True,
    ) -> dict[str, Any]:
        return self.repository.create_subscription(
            subscriber_url=subscriber_url,
            festivals=festivals,
            remind_days_before=remind_days_before,
            payload_format=payload_format,
            active=active,
        )

    def get_subscription(self, subscription_id: str) -> dict[str, Any] | None:
        return self.repository.get_subscription(subscription_id)

    def delete_subscription(self, subscription_id: str) -> bool:
        return self.repository.delete_subscription(subscription_id)

    def list_delivery_jobs(self, *, status: str | None = None) -> list[dict[str, Any]]:
        return self.queue.list_jobs(status=status)

    def list_delivery_attempts(self, job_id: str) -> list[dict[str, Any]]:
        return self.queue.list_attempts(job_id)

    async def _deliver_event(
        self,
        *,
        url: str,
        payload: dict[str, Any],
        job_id: str,
        attestation: dict[str, Any],
        dry_run: bool,
    ) -> dict[str, Any]:
        headers = delivery_headers(job_id, attestation)
        if dry_run:
            return {"status": "dry_run", "http_status": None, "error": None}

        if url.startswith("mock://"):
            if "fail" in url:
                return {"status": "failed", "http_status": 502, "error": "mock failure"}
            return {"status": "sent", "http_status": 200, "error": None}

        payload_bytes = json.dumps(payload).encode("utf-8")

        def _deliver_with_urllib() -> dict[str, Any]:
            req = urllib_request.Request(
                url=url,
                data=payload_bytes,
                headers=headers,
                method="POST",
            )
            try:
                with urllib_request.urlopen(req, timeout=10) as resp:  # nosec B310
                    return {"status": "sent", "http_status": int(resp.status), "error": None}
            except urllib_error.HTTPError as exc:
                return {"status": "failed", "http_status": int(exc.code), "error": str(exc)}
            except Exception as exc:  # pragma: no cover
                return {"status": "failed", "http_status": None, "error": str(exc)}

        try:
            if aiohttp is not None:
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, data=payload_bytes, headers=headers) as resp:
                        if 200 <= resp.status < 300:
                            return {"status": "sent", "http_status": resp.status, "error": None}
                        text = await resp.text()
                        return {
                            "status": "failed",
                            "http_status": resp.status,
                            "error": f"http_{resp.status}: {text[:240]}",
                        }
            return await asyncio.to_thread(_deliver_with_urllib)
        except Exception as exc:  # pragma: no cover
            return {"status": "failed", "http_status": None, "error": str(exc)}

    def _build_payload(
        self,
        *,
        subscription_id: str,
        festival_id: str,
        start_date: date,
        end_date: date,
        notify_date: date,
        remind_days_before: int,
    ) -> dict[str, Any]:
        return {
            "subscription_id": subscription_id,
            "festival": {
                "id": festival_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "remind_days_before": int(remind_days_before),
            "notify_date": notify_date.isoformat(),
        }

    def _enqueue_for_date(
        self,
        *,
        target_date: date,
        now_utc: datetime,
        dry_run: bool,
    ) -> dict[str, Any]:
        repo = get_repository()
        totals = {
            "date": target_date.isoformat(),
            "total_candidates": 0,
            "queued": 0,
            "already_queued": 0,
            "skipped_duplicate": 0,
            "dry_run": dry_run,
            "results": [],
        }

        for subscription in self.repository.list_active_subscriptions():
            for festival_id in subscription.get("festivals", []):
                for year in {target_date.year - 1, target_date.year, target_date.year + 1}:
                    dates = repo.get_dates(festival_id, year)
                    if not dates:
                        continue
                    for remind_days_before in subscription.get("remind_days_before", [0]):
                        notify_date = dates.start_date - timedelta(days=int(remind_days_before))
                        if notify_date != target_date:
                            continue

                        totals["total_candidates"] += 1
                        payload = self._build_payload(
                            subscription_id=subscription["id"],
                            festival_id=festival_id,
                            start_date=dates.start_date,
                            end_date=dates.end_date,
                            notify_date=notify_date,
                            remind_days_before=int(remind_days_before),
                        )
                        event_key = (
                            f"{subscription['id']}:{festival_id}:{dates.start_date.isoformat()}:"
                            f"{int(remind_days_before)}"
                        )
                        if dry_run:
                            totals["results"].append(
                                {
                                    "event_key": event_key,
                                    "subscription_id": subscription["id"],
                                    "festival_id": festival_id,
                                    "status": "dry_run",
                                    "attestation": build_webhook_attestation(payload),
                                }
                            )
                            continue

                        created, job = self.queue.enqueue(
                            subscription_id=subscription["id"],
                            subscriber_url=subscription["subscriber_url"],
                            festival_id=festival_id,
                            festival_start_date=dates.start_date.isoformat(),
                            festival_end_date=dates.end_date.isoformat(),
                            notify_date=notify_date.isoformat(),
                            remind_days_before=int(remind_days_before),
                            payload=payload,
                            now_utc=now_utc,
                        )
                        if created:
                            totals["queued"] += 1
                        elif job["status"] == "sent":
                            totals["skipped_duplicate"] += 1
                        else:
                            totals["already_queued"] += 1
                        totals["results"].append(
                            {
                                "event_key": event_key,
                                "subscription_id": subscription["id"],
                                "festival_id": festival_id,
                                "status": "queued" if created else job["status"],
                                "job_id": job["job_id"],
                                "attestation": job["attestation"],
                            }
                        )
        return totals

    async def drain_queue(
        self,
        *,
        now_utc: datetime | None = None,
        dry_run: bool = False,
        limit: int = 100,
    ) -> dict[str, Any]:
        now = now_utc or utc_now()
        due_jobs = self.queue.load_due_jobs(now_utc=now, limit=limit)
        totals = {
            "processed": len(due_jobs),
            "sent": 0,
            "retry_scheduled": 0,
            "dead_letter": 0,
            "dry_run": dry_run,
            "results": [],
        }

        for job in due_jobs:
            result = await self._deliver_event(
                url=job["subscriber_url"],
                payload=job["payload"],
                job_id=job["job_id"],
                attestation=job["attestation"],
                dry_run=dry_run,
            )
            if dry_run:
                totals["results"].append(
                    {
                        "job_id": job["job_id"],
                        "event_key": job["event_key"],
                        "status": "dry_run",
                        "attestation": job["attestation"],
                    }
                )
                continue

            if result["status"] == "sent":
                totals["sent"] += 1
                totals["results"].append(
                    self.queue.mark_sent(job=job, http_status=result["http_status"], attempted_at=now)
                )
                continue

            if int(job["attempt_count"]) + 1 >= int(job["max_attempts"]):
                totals["dead_letter"] += 1
                updated = self.queue.mark_dead_letter(
                    job=job,
                    http_status=result["http_status"],
                    error=result["error"],
                    attempted_at=now,
                )
            else:
                totals["retry_scheduled"] += 1
                updated = self.queue.mark_retry_scheduled(
                    job=job,
                    http_status=result["http_status"],
                    error=result["error"],
                    attempted_at=now,
                )
            totals["results"].append(updated)

        return totals

    async def dispatch_for_date(
        self,
        target_date: date,
        dry_run: bool = False,
        *,
        now_utc: datetime | None = None,
    ) -> dict[str, Any]:
        now = now_utc or utc_now()
        enqueue_totals = self._enqueue_for_date(target_date=target_date, now_utc=now, dry_run=dry_run)
        if dry_run:
            return enqueue_totals

        drain_totals = await self.drain_queue(now_utc=now, dry_run=False)
        return {
            **enqueue_totals,
            "sent": drain_totals["sent"],
            "retry_scheduled": drain_totals["retry_scheduled"],
            "dead_letter": drain_totals["dead_letter"],
            "results": [*enqueue_totals["results"], *drain_totals["results"]],
        }


_service: WebhookService | None = None


def get_webhook_service() -> WebhookService:
    global _service
    if _service is None:
        _service = WebhookService()
    return _service
