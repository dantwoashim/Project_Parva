"""Small database abstraction for billing state.

The production path is Postgres via psycopg. Local development and tests use
SQLite so monetization can be exercised without external infrastructure.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from .plans import PLAN_DEFINITIONS


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat()


def month_period(now: datetime | None = None) -> tuple[str, str]:
    current = now or utc_now()
    period = current.strftime("%Y-%m")
    if current.month == 12:
        reset = current.replace(year=current.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        reset = current.replace(month=current.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return period, reset.isoformat()


def day_period(now: datetime | None = None) -> tuple[str, str]:
    current = now or utc_now()
    period = current.strftime("%Y-%m-%d")
    reset = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return period, reset.isoformat()


@dataclass(frozen=True)
class DatabaseConfig:
    url: str
    dialect: str


def parse_database_url(database_url: str) -> DatabaseConfig:
    if database_url.startswith(("postgres://", "postgresql://")):
        return DatabaseConfig(url=database_url, dialect="postgres")
    if database_url.startswith("sqlite:///"):
        return DatabaseConfig(url=database_url.removeprefix("sqlite:///"), dialect="sqlite")
    if database_url == "sqlite:///:memory:":
        return DatabaseConfig(url=":memory:", dialect="sqlite")
    raise ValueError("PARVA_DATABASE_URL must be postgres://, postgresql://, or sqlite:///")


class BillingStore:
    def __init__(self, database_url: str) -> None:
        self.config = parse_database_url(database_url)
        self._memory_sqlite: sqlite3.Connection | None = None

    @contextmanager
    def connect(self) -> Iterator[Any]:
        if self.config.dialect == "sqlite":
            if self.config.url == ":memory:":
                if self._memory_sqlite is None:
                    self._memory_sqlite = sqlite3.connect(":memory:", check_same_thread=False)
                    self._memory_sqlite.row_factory = sqlite3.Row
                    self._configure_sqlite_connection(self._memory_sqlite, persistent=False)
                yield self._memory_sqlite
                self._memory_sqlite.commit()
                return

            path = Path(self.config.url)
            path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path, timeout=5.0)
            conn.row_factory = sqlite3.Row
            self._configure_sqlite_connection(conn, persistent=True)
            try:
                yield conn
                conn.commit()
            finally:
                conn.close()
            return

        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:  # pragma: no cover - only hit in Postgres deployments.
            raise RuntimeError("Postgres billing requires psycopg[binary].") from exc

        with psycopg.connect(self.config.url, row_factory=dict_row) as pg_conn:
            yield pg_conn

    @staticmethod
    def _configure_sqlite_connection(conn: sqlite3.Connection, *, persistent: bool) -> None:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        if persistent:
            conn.execute("PRAGMA journal_mode=WAL")

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        with self.connect() as conn:
            conn.execute(sql, params)

    def fetchone(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None

    def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def param(self) -> str:
        return "?" if self.config.dialect == "sqlite" else "%s"

    def migrate(self) -> None:
        from .migrations import run_migrations

        run_migrations(self)
        self.seed_plans()

    def seed_plans(self) -> None:
        for plan in PLAN_DEFINITIONS:
            features_json = json.dumps(list(plan.features), separators=(",", ":"))
            if self.config.dialect == "sqlite":
                sql = """
                INSERT INTO plans (id, slug, name, currency, price_minor, monthly_limit, daily_limit, features_json, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(slug) DO UPDATE SET
                  name=excluded.name,
                  currency=excluded.currency,
                  price_minor=excluded.price_minor,
                  monthly_limit=excluded.monthly_limit,
                  daily_limit=excluded.daily_limit,
                  features_json=excluded.features_json,
                  active=excluded.active
                """
            else:
                sql = """
                INSERT INTO plans (id, slug, name, currency, price_minor, monthly_limit, daily_limit, features_json, active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true)
                ON CONFLICT(slug) DO UPDATE SET
                  name=excluded.name,
                  currency=excluded.currency,
                  price_minor=excluded.price_minor,
                  monthly_limit=excluded.monthly_limit,
                  daily_limit=excluded.daily_limit,
                  features_json=excluded.features_json,
                  active=excluded.active
                """
            self.execute(
                sql,
                (
                    plan.slug,
                    plan.slug,
                    plan.name,
                    plan.currency,
                    plan.price_minor,
                    plan.monthly_limit,
                    plan.daily_limit,
                    features_json,
                ),
            )
