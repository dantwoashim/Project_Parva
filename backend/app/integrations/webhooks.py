"""Webhook subscription store and dispatch service."""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

try:  # Optional runtime dependency in constrained environments.
    import aiohttp
except Exception:  # pragma: no cover
    aiohttp = None

from app.festivals.repository import get_repository

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STORE_PATH = PROJECT_ROOT / "backend" / "data" / "webhooks" / "subscriptions.json"


class WebhookService:
    """JSON-backed webhook subscription service."""

    def __init__(self, store_path: Path | None = None) -> None:
        self.store_path = store_path or STORE_PATH
        self.store_path.parent.mkdir(parents=True, exist_ok=True)

    def _default_store(self) -> dict[str, Any]:
        return {
            "subscriptions": [],
            "deliveries": [],
        }

    def _load_store(self) -> dict[str, Any]:
        if not self.store_path.exists():
            return self._default_store()
        try:
            payload = json.loads(self.store_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                return self._default_store()
            payload.setdefault("subscriptions", [])
            payload.setdefault("deliveries", [])
            return payload
        except json.JSONDecodeError:
            return self._default_store()

    def _save_store(self, payload: dict[str, Any]) -> None:
        self.store_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def _validate_url(url: str) -> None:
        if url.startswith("http://") or url.startswith("https://") or url.startswith("mock://"):
            return
        raise ValueError("subscriber_url must start with http://, https://, or mock://")

    def list_subscriptions(self) -> list[dict[str, Any]]:
        store = self._load_store()
        return store["subscriptions"]

    def create_subscription(
        self,
        *,
        subscriber_url: str,
        festivals: list[str],
        remind_days_before: list[int],
        payload_format: str = "json",
        active: bool = True,
    ) -> dict[str, Any]:
        self._validate_url(subscriber_url)
        if payload_format != "json":
            raise ValueError("Only json payload_format is currently supported")
        if not festivals:
            raise ValueError("festivals must not be empty")
        if not remind_days_before:
            remind_days_before = [0]

        now = datetime.now(timezone.utc).isoformat()
        record = {
            "id": f"sub_{uuid.uuid4().hex[:10]}",
            "subscriber_url": subscriber_url,
            "festivals": sorted(set(festivals)),
            "remind_days_before": sorted(set(int(v) for v in remind_days_before)),
            "format": payload_format,
            "active": bool(active),
            "created_at": now,
            "updated_at": now,
        }

        store = self._load_store()
        store["subscriptions"].append(record)
        self._save_store(store)
        return record

    def get_subscription(self, subscription_id: str) -> dict[str, Any] | None:
        store = self._load_store()
        for row in store["subscriptions"]:
            if row["id"] == subscription_id:
                return row
        return None

    def delete_subscription(self, subscription_id: str) -> bool:
        store = self._load_store()
        before = len(store["subscriptions"])
        store["subscriptions"] = [row for row in store["subscriptions"] if row["id"] != subscription_id]
        after = len(store["subscriptions"])
        if after == before:
            return False
        self._save_store(store)
        return True

    def _already_sent(self, deliveries: list[dict[str, Any]], event_key: str) -> bool:
        for delivery in deliveries:
            if delivery.get("event_key") == event_key and delivery.get("status") == "sent":
                return True
        return False

    async def _deliver_event(self, url: str, payload: dict[str, Any], dry_run: bool) -> dict[str, Any]:
        if dry_run:
            return {"status": "dry_run", "attempts": 0, "http_status": None, "error": None}

        if url.startswith("mock://"):
            if "fail" in url:
                return {"status": "failed", "attempts": 3, "http_status": 500, "error": "mock failure"}
            return {"status": "sent", "attempts": 1, "http_status": 200, "error": None}

        def _deliver_with_urllib() -> dict[str, Any]:
            payload_bytes = json.dumps(payload).encode("utf-8")
            req = urllib_request.Request(
                url=url,
                data=payload_bytes,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib_request.urlopen(req, timeout=10) as resp:  # nosec B310
                    return {"http_status": int(resp.status), "error": None}
            except urllib_error.HTTPError as exc:
                return {"http_status": int(exc.code), "error": str(exc)}
            except Exception as exc:  # pragma: no cover
                return {"http_status": None, "error": str(exc)}

        last_error: str | None = None
        last_status: int | None = None

        for attempt in range(1, 4):
            try:
                if aiohttp is not None:
                    timeout = aiohttp.ClientTimeout(total=10)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(
                            url, json=payload, headers={"Content-Type": "application/json"}
                        ) as resp:
                            last_status = resp.status
                            if 200 <= resp.status < 300:
                                return {
                                    "status": "sent",
                                    "attempts": attempt,
                                    "http_status": resp.status,
                                    "error": None,
                                }
                            text = await resp.text()
                            last_error = f"http_{resp.status}: {text[:240]}"
                else:
                    fallback = await asyncio.to_thread(_deliver_with_urllib)
                    last_status = fallback["http_status"]
                    if last_status is not None and 200 <= last_status < 300:
                        return {
                            "status": "sent",
                            "attempts": attempt,
                            "http_status": last_status,
                            "error": None,
                        }
                    last_error = fallback["error"]
            except Exception as exc:  # pragma: no cover - network failures are nondeterministic
                last_error = str(exc)

            if attempt < 3:
                await asyncio.sleep(0.5 * (2 ** (attempt - 1)))

        return {
            "status": "failed",
            "attempts": 3,
            "http_status": last_status,
            "error": last_error,
        }

    async def dispatch_for_date(self, target_date: date, dry_run: bool = False) -> dict[str, Any]:
        repo = get_repository()
        store = self._load_store()
        deliveries = store["deliveries"]

        totals = {
            "date": target_date.isoformat(),
            "total_candidates": 0,
            "sent": 0,
            "failed": 0,
            "skipped_duplicate": 0,
            "dry_run": dry_run,
            "results": [],
        }

        for sub in store["subscriptions"]:
            if not sub.get("active", True):
                continue
            sub_id = sub["id"]
            url = sub["subscriber_url"]
            remind_values = sub.get("remind_days_before", [0])
            festivals = sub.get("festivals", [])

            for festival_id in festivals:
                for year in {target_date.year - 1, target_date.year, target_date.year + 1}:
                    dates = repo.get_dates(festival_id, year)
                    if not dates:
                        continue
                    for remind in remind_values:
                        notify_date = dates.start_date - timedelta(days=int(remind))
                        if notify_date != target_date:
                            continue

                        totals["total_candidates"] += 1
                        event_key = f"{sub_id}:{festival_id}:{dates.start_date.isoformat()}:{int(remind)}"
                        if self._already_sent(deliveries, event_key):
                            totals["skipped_duplicate"] += 1
                            totals["results"].append(
                                {
                                    "subscription_id": sub_id,
                                    "festival_id": festival_id,
                                    "event_key": event_key,
                                    "status": "skipped_duplicate",
                                }
                            )
                            continue

                        payload = {
                            "subscription_id": sub_id,
                            "festival": {
                                "id": festival_id,
                                "start_date": dates.start_date.isoformat(),
                                "end_date": dates.end_date.isoformat(),
                            },
                            "remind_days_before": int(remind),
                            "notify_date": target_date.isoformat(),
                        }

                        result = await self._deliver_event(url, payload, dry_run=dry_run)
                        if result["status"] == "sent":
                            totals["sent"] += 1
                        elif result["status"] == "failed":
                            totals["failed"] += 1

                        delivery_row = {
                            "event_key": event_key,
                            "subscription_id": sub_id,
                            "festival_id": festival_id,
                            "status": result["status"],
                            "attempts": result["attempts"],
                            "http_status": result["http_status"],
                            "error": result["error"],
                            "delivered_at": datetime.now(timezone.utc).isoformat(),
                        }
                        deliveries.append(delivery_row)
                        totals["results"].append(delivery_row)

        self._save_store(store)
        return totals


_service: WebhookService | None = None


def get_webhook_service() -> WebhookService:
    global _service
    if _service is None:
        _service = WebhookService()
    return _service
