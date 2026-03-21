"""Persistent store primitives for webhook subscriptions and queued deliveries."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import socket
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.provenance.attestation import canonical_json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
WEBHOOKS_DIR = PROJECT_ROOT / "backend" / "data" / "webhooks"
DB_PATH = WEBHOOKS_DIR / "webhooks.sqlite3"
LEGACY_STORE_PATH = WEBHOOKS_DIR / "subscriptions.json"
DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_RETRY_BASE_SECONDS = 30


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def json_dump(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def allow_insecure_http() -> bool:
    return os.getenv("PARVA_WEBHOOK_ALLOW_INSECURE_HTTP", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def webhook_signing_key() -> bytes | None:
    raw = os.getenv("PARVA_WEBHOOK_SIGNING_KEY", "").strip()
    if not raw:
        return None
    return raw.encode("utf-8")


def webhook_signing_key_id() -> str | None:
    raw = os.getenv("PARVA_WEBHOOK_SIGNING_KEY_ID", "").strip()
    return raw or None


def build_webhook_attestation(payload: dict[str, Any]) -> dict[str, Any]:
    key = webhook_signing_key()
    if not key:
        return {
            "mode": "unsigned",
            "algorithm": None,
            "key_id": None,
            "value": None,
        }

    value = hmac.new(key, canonical_json(payload).encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "mode": "hmac-sha256",
        "algorithm": "hmac-sha256",
        "key_id": webhook_signing_key_id() or "webhook-local-hmac",
        "value": value,
    }


def delivery_headers(job_id: str, attestation: dict[str, Any]) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "X-Parva-Webhook-Id": job_id,
        "X-Parva-Webhook-Attestation-Mode": str(attestation.get("mode") or "unsigned"),
    }
    if attestation.get("key_id"):
        headers["X-Parva-Webhook-Key-Id"] = str(attestation["key_id"])
    if attestation.get("value"):
        algorithm = str(attestation.get("algorithm") or "hmac-sha256")
        headers["X-Parva-Webhook-Attestation"] = f"{algorithm}={attestation['value']}"
    return headers


def host_looks_internal(host: str) -> bool:
    normalized = host.strip().lower().rstrip(".")
    if normalized in {"localhost", "localhost.localdomain"}:
        return True
    if normalized.endswith((".internal", ".local", ".localhost", ".home", ".lan")):
        return True
    if "." not in normalized:
        return True
    return False


def address_is_disallowed(value: str) -> bool:
    try:
        parsed = ip_address(value)
    except ValueError:
        return False
    return not parsed.is_global


def resolve_host_addresses(host: str) -> list[str]:
    try:
        results = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except OSError:
        return []
    return sorted({row[4][0] for row in results if row and row[4]})


def validate_public_target(host: str) -> None:
    if not host:
        raise ValueError("subscriber_url must include a hostname")
    if host_looks_internal(host):
        raise ValueError("subscriber_url must not target localhost or internal-only hostnames")
    if address_is_disallowed(host):
        raise ValueError("subscriber_url must not target private, loopback, or reserved IP ranges")
    for resolved in resolve_host_addresses(host):
        if address_is_disallowed(resolved):
            raise ValueError(
                "subscriber_url must not resolve to private, loopback, or reserved IP ranges"
            )


def validate_subscriber_url(url: str) -> None:
    if url.startswith("mock://"):
        return

    parsed = urlparse(url)
    if parsed.scheme not in {"https", "http"}:
        raise ValueError("subscriber_url must start with https:// or mock://")
    if parsed.scheme != "https" and not allow_insecure_http():
        raise ValueError(
            "subscriber_url must use https:// unless PARVA_WEBHOOK_ALLOW_INSECURE_HTTP=true"
        )
    validate_public_target(parsed.hostname or "")


def normalize_subscription_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "subscriber_url": row["subscriber_url"],
        "festivals": json.loads(row["festivals_json"]),
        "remind_days_before": json.loads(row["remind_days_before_json"]),
        "format": row["payload_format"],
        "active": bool(row["active"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def normalize_job_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "job_id": row["job_id"],
        "event_key": row["event_key"],
        "subscription_id": row["subscription_id"],
        "subscriber_url": row["subscriber_url"],
        "festival_id": row["festival_id"],
        "festival_start_date": row["festival_start_date"],
        "festival_end_date": row["festival_end_date"],
        "notify_date": row["notify_date"],
        "remind_days_before": row["remind_days_before"],
        "payload": json.loads(row["payload_json"]),
        "status": row["status"],
        "attempt_count": row["attempt_count"],
        "max_attempts": row["max_attempts"],
        "next_attempt_at": row["next_attempt_at"],
        "last_http_status": row["last_http_status"],
        "last_error": row["last_error"],
        "attestation": json.loads(row["attestation_json"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "dispatched_at": row["dispatched_at"],
        "dead_lettered_at": row["dead_lettered_at"],
    }


def normalize_attempt_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "attempt_id": row["attempt_id"],
        "job_id": row["job_id"],
        "attempt_number": row["attempt_number"],
        "status": row["status"],
        "http_status": row["http_status"],
        "error": row["error"],
        "attestation": json.loads(row["attestation_json"]),
        "attempted_at": row["attempted_at"],
    }


def legacy_payload_for_event(
    *,
    subscription_id: str,
    festival_id: str,
    start_date: str,
    notify_date: str,
    remind_days_before: int,
) -> dict[str, Any]:
    return {
        "subscription_id": subscription_id,
        "festival": {
            "id": festival_id,
            "start_date": start_date,
            "end_date": start_date,
        },
        "remind_days_before": remind_days_before,
        "notify_date": notify_date,
    }


@dataclass
class WebhookStore:
    db_path: Path = DB_PATH
    legacy_store_path: Path = LEGACY_STORE_PATH

    def __post_init__(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()
        self._migrate_legacy_json_if_needed()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        schema = """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS subscriptions (
            id TEXT PRIMARY KEY,
            subscriber_url TEXT NOT NULL,
            festivals_json TEXT NOT NULL,
            remind_days_before_json TEXT NOT NULL,
            payload_format TEXT NOT NULL,
            active INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS delivery_jobs (
            job_id TEXT PRIMARY KEY,
            event_key TEXT NOT NULL UNIQUE,
            subscription_id TEXT NOT NULL,
            subscriber_url TEXT NOT NULL,
            festival_id TEXT NOT NULL,
            festival_start_date TEXT NOT NULL,
            festival_end_date TEXT NOT NULL,
            notify_date TEXT NOT NULL,
            remind_days_before INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            status TEXT NOT NULL,
            attempt_count INTEGER NOT NULL,
            max_attempts INTEGER NOT NULL,
            next_attempt_at TEXT NOT NULL,
            last_http_status INTEGER,
            last_error TEXT,
            attestation_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            dispatched_at TEXT,
            dead_lettered_at TEXT
        );

        CREATE TABLE IF NOT EXISTS delivery_attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            attempt_number INTEGER NOT NULL,
            status TEXT NOT NULL,
            http_status INTEGER,
            error TEXT,
            attestation_json TEXT NOT NULL,
            attempted_at TEXT NOT NULL
        );
        """
        with self.connect() as conn:
            conn.executescript(schema)

    def meta_get(self, key: str) -> str | None:
        with self.connect() as conn:
            row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return str(row["value"]) if row else None

    def meta_set(self, key: str, value: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def _migrate_legacy_json_if_needed(self) -> None:
        if self.meta_get("legacy_json_migrated"):
            return
        if not self.legacy_store_path.exists():
            self.meta_set("legacy_json_migrated", "absent")
            return

        try:
            payload = json.loads(self.legacy_store_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self.meta_set("legacy_json_migrated", "invalid_json")
            return

        subscriptions = payload.get("subscriptions") if isinstance(payload, dict) else []
        deliveries = payload.get("deliveries") if isinstance(payload, dict) else []
        subscriptions = subscriptions if isinstance(subscriptions, list) else []
        deliveries = deliveries if isinstance(deliveries, list) else []

        with self.connect() as conn:
            subscription_count = conn.execute("SELECT COUNT(*) FROM subscriptions").fetchone()[0]
            job_count = conn.execute("SELECT COUNT(*) FROM delivery_jobs").fetchone()[0]

            if subscription_count == 0:
                for row in subscriptions:
                    if not isinstance(row, dict) or not row.get("id") or not row.get("subscriber_url"):
                        continue
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO subscriptions (
                            id, subscriber_url, festivals_json, remind_days_before_json,
                            payload_format, active, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            str(row["id"]),
                            str(row["subscriber_url"]),
                            json_dump(sorted(set(str(item) for item in row.get("festivals") or []))),
                            json_dump(
                                sorted(
                                    set(int(item) for item in (row.get("remind_days_before") or [0]))
                                )
                            ),
                            str(row.get("format") or "json"),
                            1 if row.get("active", True) else 0,
                            str(row.get("created_at") or to_iso(utc_now())),
                            str(row.get("updated_at") or row.get("created_at") or to_iso(utc_now())),
                        ),
                    )

            if job_count == 0:
                subscription_urls = {
                    row["id"]: row["subscriber_url"]
                    for row in conn.execute("SELECT id, subscriber_url FROM subscriptions")
                }
                for row in deliveries:
                    if not isinstance(row, dict):
                        continue
                    event_key = str(row.get("event_key") or "").strip()
                    subscription_id = str(row.get("subscription_id") or "").strip()
                    festival_id = str(row.get("festival_id") or "").strip()
                    if not event_key or not subscription_id or not festival_id:
                        continue
                    try:
                        _, _, start_date, remind_raw = event_key.split(":", 3)
                        remind_days = int(remind_raw)
                    except (TypeError, ValueError):
                        start_date = str(
                            row.get("festival_start_date")
                            or row.get("notify_date")
                            or utc_now().date().isoformat()
                        )
                        remind_days = 0
                    delivered_at = str(row.get("delivered_at") or to_iso(utc_now()))
                    notify_date = delivered_at[:10]
                    status = "sent" if str(row.get("status") or "") == "sent" else "dead_letter"
                    payload_json = legacy_payload_for_event(
                        subscription_id=subscription_id,
                        festival_id=festival_id,
                        start_date=start_date,
                        notify_date=notify_date,
                        remind_days_before=remind_days,
                    )
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO delivery_jobs (
                            job_id, event_key, subscription_id, subscriber_url, festival_id,
                            festival_start_date, festival_end_date, notify_date, remind_days_before,
                            payload_json, status, attempt_count, max_attempts, next_attempt_at,
                            last_http_status, last_error, attestation_json, created_at, updated_at,
                            dispatched_at, dead_lettered_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            f"job_{uuid.uuid4().hex[:16]}",
                            event_key,
                            subscription_id,
                            subscription_urls.get(subscription_id, "migrated://unknown"),
                            festival_id,
                            start_date,
                            start_date,
                            notify_date,
                            remind_days,
                            json_dump(payload_json),
                            status,
                            int(row.get("attempts") or 0),
                            DEFAULT_MAX_ATTEMPTS,
                            delivered_at,
                            row.get("http_status"),
                            row.get("error"),
                            json_dump(
                                {
                                    "mode": "legacy-import",
                                    "algorithm": None,
                                    "key_id": None,
                                    "value": None,
                                }
                            ),
                            delivered_at,
                            delivered_at,
                            delivered_at if status == "sent" else None,
                            delivered_at if status == "dead_letter" else None,
                        ),
                    )
            conn.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                ("legacy_json_migrated", "done"),
            )


class WebhookSubscriptionRepository:
    """Durable subscription repository backed by SQLite."""

    def __init__(self, store: WebhookStore) -> None:
        self.store = store

    def list_subscriptions(self) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM subscriptions ORDER BY created_at ASC, id ASC"
            ).fetchall()
        return [normalize_subscription_row(row) for row in rows]

    def list_active_subscriptions(self) -> list[dict[str, Any]]:
        return [row for row in self.list_subscriptions() if row["active"]]

    def create_subscription(
        self,
        *,
        subscriber_url: str,
        festivals: list[str],
        remind_days_before: list[int],
        payload_format: str = "json",
        active: bool = True,
    ) -> dict[str, Any]:
        validate_subscriber_url(subscriber_url)
        if payload_format != "json":
            raise ValueError("Only json payload_format is currently supported")
        if not festivals:
            raise ValueError("festivals must not be empty")
        if not remind_days_before:
            remind_days_before = [0]

        now = to_iso(utc_now())
        record = {
            "id": f"sub_{uuid.uuid4().hex[:10]}",
            "subscriber_url": subscriber_url,
            "festivals": sorted({str(value).strip() for value in festivals if str(value).strip()}),
            "remind_days_before": sorted({int(value) for value in remind_days_before}),
            "format": payload_format,
            "active": bool(active),
            "created_at": now,
            "updated_at": now,
        }
        if not record["festivals"]:
            raise ValueError("festivals must not be empty")

        with self.store.connect() as conn:
            conn.execute(
                """
                INSERT INTO subscriptions (
                    id, subscriber_url, festivals_json, remind_days_before_json,
                    payload_format, active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["id"],
                    record["subscriber_url"],
                    json_dump(record["festivals"]),
                    json_dump(record["remind_days_before"]),
                    record["format"],
                    1 if record["active"] else 0,
                    record["created_at"],
                    record["updated_at"],
                ),
            )
        return record

    def get_subscription(self, subscription_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT * FROM subscriptions WHERE id = ?",
                (subscription_id,),
            ).fetchone()
        return normalize_subscription_row(row) if row else None

    def delete_subscription(self, subscription_id: str) -> bool:
        with self.store.connect() as conn:
            deleted = conn.execute(
                "DELETE FROM subscriptions WHERE id = ?",
                (subscription_id,),
            ).rowcount
        return deleted > 0


class WebhookDeliveryQueue:
    """Persistent queued delivery state with retry and dead-letter handling."""

    def __init__(
        self,
        store: WebhookStore,
        *,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        retry_base_seconds: int = DEFAULT_RETRY_BASE_SECONDS,
    ) -> None:
        self.store = store
        self.max_attempts = max(1, int(max_attempts))
        self.retry_base_seconds = max(1, int(retry_base_seconds))

    def enqueue(
        self,
        *,
        subscription_id: str,
        subscriber_url: str,
        festival_id: str,
        festival_start_date: str,
        festival_end_date: str,
        notify_date: str,
        remind_days_before: int,
        payload: dict[str, Any],
        now_utc: datetime | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        now = to_iso(now_utc or utc_now())
        event_key = f"{subscription_id}:{festival_id}:{festival_start_date}:{int(remind_days_before)}"

        with self.store.connect() as conn:
            existing = conn.execute(
                "SELECT * FROM delivery_jobs WHERE event_key = ?",
                (event_key,),
            ).fetchone()
            if existing:
                return False, normalize_job_row(existing)

            job = {
                "job_id": f"job_{uuid.uuid4().hex[:16]}",
                "event_key": event_key,
                "subscription_id": subscription_id,
                "subscriber_url": subscriber_url,
                "festival_id": festival_id,
                "festival_start_date": festival_start_date,
                "festival_end_date": festival_end_date,
                "notify_date": notify_date,
                "remind_days_before": int(remind_days_before),
                "payload": payload,
                "status": "pending",
                "attempt_count": 0,
                "max_attempts": self.max_attempts,
                "next_attempt_at": now,
                "last_http_status": None,
                "last_error": None,
                "attestation": build_webhook_attestation(payload),
                "created_at": now,
                "updated_at": now,
                "dispatched_at": None,
                "dead_lettered_at": None,
            }
            conn.execute(
                """
                INSERT INTO delivery_jobs (
                    job_id, event_key, subscription_id, subscriber_url, festival_id,
                    festival_start_date, festival_end_date, notify_date, remind_days_before,
                    payload_json, status, attempt_count, max_attempts, next_attempt_at,
                    last_http_status, last_error, attestation_json, created_at, updated_at,
                    dispatched_at, dead_lettered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job["job_id"],
                    job["event_key"],
                    job["subscription_id"],
                    job["subscriber_url"],
                    job["festival_id"],
                    job["festival_start_date"],
                    job["festival_end_date"],
                    job["notify_date"],
                    job["remind_days_before"],
                    json_dump(job["payload"]),
                    job["status"],
                    job["attempt_count"],
                    job["max_attempts"],
                    job["next_attempt_at"],
                    job["last_http_status"],
                    job["last_error"],
                    json_dump(job["attestation"]),
                    job["created_at"],
                    job["updated_at"],
                    job["dispatched_at"],
                    job["dead_lettered_at"],
                ),
            )
        return True, job

    def list_jobs(self, *, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM delivery_jobs"
        params: tuple[Any, ...] = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY created_at ASC, job_id ASC"
        with self.store.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [normalize_job_row(row) for row in rows]

    def list_attempts(self, job_id: str) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM delivery_attempts WHERE job_id = ? ORDER BY attempt_number ASC",
                (job_id,),
            ).fetchall()
        return [normalize_attempt_row(row) for row in rows]

    def load_due_jobs(self, *, now_utc: datetime | None = None, limit: int = 100) -> list[dict[str, Any]]:
        now = to_iso(now_utc or utc_now())
        with self.store.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM delivery_jobs
                WHERE status IN ('pending', 'retry_scheduled')
                  AND next_attempt_at <= ?
                ORDER BY next_attempt_at ASC, created_at ASC
                LIMIT ?
                """,
                (now, int(limit)),
            ).fetchall()
        return [normalize_job_row(row) for row in rows]

    def _record_attempt(
        self,
        *,
        job_id: str,
        attempt_number: int,
        status: str,
        http_status: int | None,
        error: str | None,
        attestation: dict[str, Any],
        attempted_at: str,
    ) -> None:
        with self.store.connect() as conn:
            conn.execute(
                """
                INSERT INTO delivery_attempts (
                    job_id, attempt_number, status, http_status, error, attestation_json, attempted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    attempt_number,
                    status,
                    http_status,
                    error,
                    json_dump(attestation),
                    attempted_at,
                ),
            )

    def mark_sent(
        self,
        *,
        job: dict[str, Any],
        http_status: int | None,
        attempted_at: datetime,
    ) -> dict[str, Any]:
        attempt_number = int(job["attempt_count"]) + 1
        attempted_at_iso = to_iso(attempted_at)
        self._record_attempt(
            job_id=job["job_id"],
            attempt_number=attempt_number,
            status="sent",
            http_status=http_status,
            error=None,
            attestation=job["attestation"],
            attempted_at=attempted_at_iso,
        )
        with self.store.connect() as conn:
            conn.execute(
                """
                UPDATE delivery_jobs
                SET status = 'sent',
                    attempt_count = ?,
                    last_http_status = ?,
                    last_error = NULL,
                    updated_at = ?,
                    dispatched_at = ?
                WHERE job_id = ?
                """,
                (attempt_number, http_status, attempted_at_iso, attempted_at_iso, job["job_id"]),
            )
            row = conn.execute(
                "SELECT * FROM delivery_jobs WHERE job_id = ?",
                (job["job_id"],),
            ).fetchone()
        return normalize_job_row(row)

    def mark_retry_scheduled(
        self,
        *,
        job: dict[str, Any],
        http_status: int | None,
        error: str | None,
        attempted_at: datetime,
    ) -> dict[str, Any]:
        attempt_number = int(job["attempt_count"]) + 1
        attempted_at_iso = to_iso(attempted_at)
        next_attempt_at = attempted_at + timedelta(
            seconds=self.retry_base_seconds * (2 ** max(0, attempt_number - 1))
        )
        next_attempt_iso = to_iso(next_attempt_at)
        self._record_attempt(
            job_id=job["job_id"],
            attempt_number=attempt_number,
            status="retry_scheduled",
            http_status=http_status,
            error=error,
            attestation=job["attestation"],
            attempted_at=attempted_at_iso,
        )
        with self.store.connect() as conn:
            conn.execute(
                """
                UPDATE delivery_jobs
                SET status = 'retry_scheduled',
                    attempt_count = ?,
                    last_http_status = ?,
                    last_error = ?,
                    next_attempt_at = ?,
                    updated_at = ?
                WHERE job_id = ?
                """,
                (
                    attempt_number,
                    http_status,
                    error,
                    next_attempt_iso,
                    attempted_at_iso,
                    job["job_id"],
                ),
            )
            row = conn.execute(
                "SELECT * FROM delivery_jobs WHERE job_id = ?",
                (job["job_id"],),
            ).fetchone()
        return normalize_job_row(row)

    def mark_dead_letter(
        self,
        *,
        job: dict[str, Any],
        http_status: int | None,
        error: str | None,
        attempted_at: datetime,
    ) -> dict[str, Any]:
        attempt_number = int(job["attempt_count"]) + 1
        attempted_at_iso = to_iso(attempted_at)
        self._record_attempt(
            job_id=job["job_id"],
            attempt_number=attempt_number,
            status="dead_letter",
            http_status=http_status,
            error=error,
            attestation=job["attestation"],
            attempted_at=attempted_at_iso,
        )
        with self.store.connect() as conn:
            conn.execute(
                """
                UPDATE delivery_jobs
                SET status = 'dead_letter',
                    attempt_count = ?,
                    last_http_status = ?,
                    last_error = ?,
                    updated_at = ?,
                    dead_lettered_at = ?
                WHERE job_id = ?
                """,
                (
                    attempt_number,
                    http_status,
                    error,
                    attempted_at_iso,
                    attempted_at_iso,
                    job["job_id"],
                ),
            )
            row = conn.execute(
                "SELECT * FROM delivery_jobs WHERE job_id = ?",
                (job["job_id"],),
            ).fetchone()
        return normalize_job_row(row)
