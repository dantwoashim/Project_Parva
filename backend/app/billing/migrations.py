"""Versioned billing schema migrations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    sqlite: tuple[str, ...]
    postgres: tuple[str, ...]


SQLITE_SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS billing_schema_migrations (
      version INTEGER PRIMARY KEY,
      name TEXT NOT NULL,
      applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS customers (
      id TEXT PRIMARY KEY,
      email TEXT NOT NULL UNIQUE,
      name TEXT,
      company_name TEXT,
      country TEXT,
      phone TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS plans (
      id TEXT PRIMARY KEY,
      slug TEXT NOT NULL UNIQUE,
      name TEXT NOT NULL,
      currency TEXT NOT NULL,
      price_minor INTEGER NOT NULL,
      monthly_limit INTEGER NOT NULL,
      daily_limit INTEGER,
      features_json TEXT NOT NULL,
      active INTEGER NOT NULL DEFAULT 1
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS subscriptions (
      id TEXT PRIMARY KEY,
      customer_id TEXT NOT NULL REFERENCES customers(id),
      plan_id TEXT NOT NULL REFERENCES plans(id),
      status TEXT NOT NULL,
      starts_at TEXT,
      renews_at TEXT,
      ends_at TEXT,
      cancelled_at TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS api_keys (
      id TEXT PRIMARY KEY,
      customer_id TEXT NOT NULL REFERENCES customers(id),
      subscription_id TEXT REFERENCES subscriptions(id),
      key_prefix TEXT NOT NULL UNIQUE,
      key_hash TEXT NOT NULL UNIQUE,
      name TEXT,
      tier TEXT NOT NULL DEFAULT 'starter',
      monthly_limit INTEGER NOT NULL,
      active INTEGER NOT NULL DEFAULT 1,
      last_used_at TEXT,
      created_at TEXT NOT NULL,
      revoked_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usage_events (
      id TEXT PRIMARY KEY,
      api_key_id TEXT,
      customer_id TEXT,
      period_ym TEXT NOT NULL,
      route_family TEXT NOT NULL,
      status_code INTEGER,
      request_id TEXT,
      created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usage_counters (
      subject_type TEXT NOT NULL,
      subject_id TEXT NOT NULL,
      period TEXT NOT NULL,
      bucket TEXT NOT NULL,
      count INTEGER NOT NULL DEFAULT 0,
      reset_at TEXT NOT NULL,
      PRIMARY KEY (subject_type, subject_id, period, bucket)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS payments (
      id TEXT PRIMARY KEY,
      customer_id TEXT NOT NULL REFERENCES customers(id),
      provider TEXT NOT NULL,
      provider_payment_id TEXT,
      provider_reference TEXT,
      amount_minor INTEGER NOT NULL,
      currency TEXT NOT NULL,
      status TEXT NOT NULL,
      verified_at TEXT,
      raw_payload_json TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS invoices (
      id TEXT PRIMARY KEY,
      customer_id TEXT NOT NULL REFERENCES customers(id),
      subscription_id TEXT REFERENCES subscriptions(id),
      invoice_number TEXT NOT NULL UNIQUE,
      amount_minor INTEGER NOT NULL,
      currency TEXT NOT NULL,
      status TEXT NOT NULL,
      due_at TEXT,
      paid_at TEXT,
      provider TEXT,
      notes TEXT,
      payment_id TEXT REFERENCES payments(id),
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS webhook_subscriptions (
      id TEXT PRIMARY KEY,
      customer_id TEXT NOT NULL REFERENCES customers(id),
      api_key_id TEXT REFERENCES api_keys(id),
      url TEXT NOT NULL,
      secret_hash TEXT NOT NULL,
      event_types TEXT NOT NULL,
      active INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_usage_events_subject ON usage_events(api_key_id, customer_id, period_ym)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_payments_reference ON payments(provider, provider_payment_id, provider_reference)
    """,
)

POSTGRES_SCHEMA = tuple(
    statement
    .replace("INTEGER PRIMARY KEY", "INTEGER PRIMARY KEY")
    .replace("TEXT PRIMARY KEY", "TEXT PRIMARY KEY")
    .replace(" active INTEGER NOT NULL DEFAULT 1", " active BOOLEAN NOT NULL DEFAULT true")
    .replace(" active INTEGER NOT NULL DEFAULT 1,", " active BOOLEAN NOT NULL DEFAULT true,")
    for statement in SQLITE_SCHEMA
)

MIGRATIONS: tuple[Migration, ...] = (
    Migration(version=1, name="billing_foundation", sqlite=SQLITE_SCHEMA, postgres=POSTGRES_SCHEMA),
)


def run_migrations(store) -> None:
    schema = SQLITE_SCHEMA[0] if store.config.dialect == "sqlite" else POSTGRES_SCHEMA[0]
    store.execute(schema)
    for migration in MIGRATIONS:
        existing = store.fetchone(
            f"SELECT version FROM billing_schema_migrations WHERE version = {store.param()}",
            (migration.version,),
        )
        if existing:
            continue
        statements = migration.sqlite if store.config.dialect == "sqlite" else migration.postgres
        for statement in statements:
            store.execute(statement)
        store.execute(
            f"INSERT INTO billing_schema_migrations (version, name) VALUES ({store.param()}, {store.param()})",
            (migration.version, migration.name),
        )

