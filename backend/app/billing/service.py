"""Billing orchestration for API keys, quotas, invoices, and payments."""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from app.security.pii import scrub_structured_trace

from .keys import (
    generate_api_key,
    hash_api_key_secret,
    parse_api_key,
    verify_api_key_secret,
)
from .storage import BillingStore, day_period, iso_now, month_period, utc_now

ACTIVE_PAYMENT_STATUSES = {"completed", "paid", "success", "verified"}
FAILED_PAYMENT_STATUSES = {"failed", "expired", "canceled", "cancelled", "refunded", "user canceled"}
MANUAL_PAYMENT_PROVIDERS = {
    "manual_qr",
    "manual_bank_qr",
    "manual_esewa_qr",
    "manual_khalti_qr",
    "manual_contact",
    "payoneer",
}
AUTOMATED_PAYMENT_PROVIDERS = {"khalti", "esewa"}


@dataclass(frozen=True)
class BillingAuthError(Exception):
    status_code: int
    detail: str


@dataclass(frozen=True)
class QuotaDecision:
    allowed: bool
    limit: int
    remaining: int
    reset_at: str
    tier: str
    detail: str | None = None


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _normalize_email(email: str) -> str:
    return str(email or "").strip().lower()


def _bool(value: Any) -> bool:
    return bool(value) and value not in {0, "0", "false", "False"}


def _invoice_number() -> str:
    now = utc_now()
    return f"PARVA-{now:%Y-%m}-{secrets.randbelow(1_000_000):06d}"


def _canonical_hash(payload: Any) -> str | None:
    if payload is None:
        return None
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class BillingService:
    def __init__(self, settings: Any) -> None:
        if not settings.database_url:
            raise RuntimeError("Billing requires PARVA_DATABASE_URL.")
        self.settings = settings
        self.store = BillingStore(settings.database_url)
        self.store.migrate()

    def health(self) -> dict[str, Any]:
        return {
            "enabled": True,
            "database": self.store.config.dialect,
            "plans": self.list_plans(),
        }

    def _active_sql(self, column: str = "active") -> str:
        return f"{column} = true" if self.store.config.dialect == "postgres" else f"{column} = 1"

    def record_audit_event(
        self,
        *,
        action: str,
        object_type: str,
        object_id: str,
        actor_principal: str | None = None,
        route: str | None = None,
        request_id: str | None = None,
        source_ip: str | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = iso_now()
        event_id = _new_id("audit")
        scrubbed_metadata = scrub_structured_trace(metadata or {})
        self.store.execute(
            f"""
            INSERT INTO billing_audit_events (
              id, action, actor_principal, route, object_type, object_id,
              before_hash, after_hash, request_id, source_ip, metadata_json, created_at
            )
            VALUES (
              {self.store.param()}, {self.store.param()}, {self.store.param()},
              {self.store.param()}, {self.store.param()}, {self.store.param()},
              {self.store.param()}, {self.store.param()}, {self.store.param()},
              {self.store.param()}, {self.store.param()}, {self.store.param()}
            )
            """,
            (
                event_id,
                action,
                actor_principal,
                route,
                object_type,
                object_id,
                _canonical_hash(before),
                _canonical_hash(after),
                request_id,
                source_ip,
                json.dumps(scrubbed_metadata, separators=(",", ":")),
                now,
            ),
        )
        return {
            "id": event_id,
            "action": action,
            "object_type": object_type,
            "object_id": object_id,
            "before_hash": _canonical_hash(before),
            "after_hash": _canonical_hash(after),
            "created_at": now,
        }

    def audit_events_for_object(self, *, object_type: str, object_id: str) -> list[dict[str, Any]]:
        return self.store.fetchall(
            f"""
            SELECT * FROM billing_audit_events
            WHERE object_type = {self.store.param()} AND object_id = {self.store.param()}
            ORDER BY created_at ASC
            """,
            (object_type, object_id),
        )

    def list_plans(self) -> list[dict[str, Any]]:
        rows = self.store.fetchall(f"SELECT * FROM plans WHERE {self._active_sql()} ORDER BY price_minor ASC")
        for row in rows:
            row["features"] = json.loads(row.pop("features_json") or "[]")
        return rows

    def get_plan(self, slug: str) -> dict[str, Any] | None:
        plan = self.store.fetchone(
            f"SELECT * FROM plans WHERE slug = {self.store.param()} AND {self._active_sql()}",
            (slug,),
        )
        if plan and "features_json" in plan:
            plan["features"] = json.loads(plan.pop("features_json") or "[]")
        return plan

    def upsert_customer(
        self,
        *,
        email: str,
        name: str | None = None,
        company_name: str | None = None,
        country: str | None = None,
        phone: str | None = None,
    ) -> dict[str, Any]:
        normalized_email = _normalize_email(email)
        if not normalized_email or "@" not in normalized_email:
            raise ValueError("A valid email is required.")
        existing = self.store.fetchone(
            f"SELECT * FROM customers WHERE email = {self.store.param()}",
            (normalized_email,),
        )
        now = iso_now()
        if existing:
            self.store.execute(
                f"""
                UPDATE customers
                SET name = COALESCE({self.store.param()}, name),
                    company_name = COALESCE({self.store.param()}, company_name),
                    country = COALESCE({self.store.param()}, country),
                    phone = COALESCE({self.store.param()}, phone),
                    updated_at = {self.store.param()}
                WHERE id = {self.store.param()}
                """,
                (name, company_name, country, phone, now, existing["id"]),
            )
            return self.store.fetchone(f"SELECT * FROM customers WHERE id = {self.store.param()}", (existing["id"],)) or existing

        customer_id = _new_id("cus")
        self.store.execute(
            f"""
            INSERT INTO customers (id, email, name, company_name, country, phone, created_at, updated_at)
            VALUES ({self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()})
            """,
            (customer_id, normalized_email, name, company_name, country, phone, now, now),
        )
        return self.store.fetchone(f"SELECT * FROM customers WHERE id = {self.store.param()}", (customer_id,)) or {}

    def create_checkout(
        self,
        *,
        email: str,
        tier: str,
        provider: str,
        name: str | None = None,
        company_name: str | None = None,
        country: str | None = None,
        phone: str | None = None,
    ) -> dict[str, Any]:
        provider_slug = str(provider or "").strip().lower()
        if provider_slug not in MANUAL_PAYMENT_PROVIDERS | AUTOMATED_PAYMENT_PROVIDERS:
            raise ValueError(
                "Provider must be manual_bank_qr, manual_esewa_qr, manual_khalti_qr, "
                "manual_contact, payoneer, khalti, or esewa."
            )
        plan = self.get_plan(tier)
        if not plan or plan["slug"] in {"free"}:
            raise ValueError("A paid tier is required for checkout.")

        customer = self.upsert_customer(
            email=email,
            name=name,
            company_name=company_name,
            country=country,
            phone=phone,
        )
        now = iso_now()
        subscription_id = _new_id("sub")
        payment_id = _new_id("pay")
        invoice_id = _new_id("inv")
        provider_payment_id = _new_id(provider_slug)
        invoice_number = _invoice_number()
        due_at = (utc_now() + timedelta(days=7)).isoformat()
        self.store.execute(
            f"""
            INSERT INTO subscriptions (id, customer_id, plan_id, status, created_at, updated_at)
            VALUES ({self.store.param()}, {self.store.param()}, {self.store.param()}, 'pending_payment', {self.store.param()}, {self.store.param()})
            """,
            (subscription_id, customer["id"], plan["id"], now, now),
        )
        self.store.execute(
            f"""
            INSERT INTO payments (id, customer_id, provider, provider_payment_id, amount_minor, currency, status, raw_payload_json, created_at, updated_at)
            VALUES ({self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, 'pending', {self.store.param()}, {self.store.param()}, {self.store.param()})
            """,
            (
                payment_id,
                customer["id"],
                provider_slug,
                provider_payment_id,
                plan["price_minor"],
                plan["currency"],
                json.dumps({"plan": plan["slug"]}),
                now,
                now,
            ),
        )
        self.store.execute(
            f"""
            INSERT INTO invoices (id, customer_id, subscription_id, invoice_number, amount_minor, currency, status, due_at, provider, payment_id, created_at, updated_at)
            VALUES ({self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, 'pending', {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()})
            """,
            (
                invoice_id,
                customer["id"],
                subscription_id,
                invoice_number,
                plan["price_minor"],
                plan["currency"],
                due_at,
                provider_slug,
                payment_id,
                now,
                now,
            ),
        )
        checkout_url = None
        if provider_slug == "khalti":
            checkout_url = self._khalti_checkout_url(provider_payment_id)
        elif provider_slug == "esewa":
            checkout_url = self._esewa_checkout_url(provider_payment_id)
        is_manual = provider_slug in MANUAL_PAYMENT_PROVIDERS

        return {
            "checkout_id": payment_id,
            "claim_token": self._claim_token_for_checkout(payment_id),
            "customer_id": customer["id"],
            "subscription_id": subscription_id,
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "provider": provider_slug,
            "status": "manual_invoice" if is_manual else "pending",
            "checkout_url": checkout_url,
            "amount_minor": plan["price_minor"],
            "currency": plan["currency"],
            "tier": plan["slug"],
            "message": (
                "Manual payment request created. Send the QR/contact payment reference to Parva support; admin confirmation activates access."
                if is_manual
                else "Payment is pending verification. Access activates only after provider lookup confirms completion."
            ),
        }

    def _khalti_checkout_url(self, payment_reference: str) -> str:
        if self.settings.khalti_public_key:
            return f"{self.settings.khalti_base_url}/epayment/initiate/?purchase_order_id={payment_reference}"
        return f"/pricing/checkout/{payment_reference}?provider=khalti"

    def _esewa_checkout_url(self, payment_reference: str) -> str:
        if self.settings.esewa_merchant_id:
            return f"{self.settings.esewa_base_url}/epay/main?pid={payment_reference}"
        return f"/pricing/checkout/{payment_reference}?provider=esewa"

    def _claim_token_for_checkout(self, checkout_id: str) -> str:
        digest = hmac.new(
            self.settings.api_key_pepper.encode("utf-8"),
            f"checkout-claim:{checkout_id}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return f"claim_{digest}"

    def get_checkout(self, checkout_id: str) -> dict[str, Any] | None:
        row = self.store.fetchone(
            f"""
            SELECT payments.*, invoices.id AS invoice_id, invoices.invoice_number,
                   invoices.status AS invoice_status, subscriptions.id AS subscription_id,
                   subscriptions.status AS subscription_status, plans.slug AS tier,
                   plans.monthly_limit
            FROM payments
            JOIN invoices ON invoices.payment_id = payments.id
            JOIN subscriptions ON subscriptions.id = invoices.subscription_id
            JOIN plans ON plans.id = subscriptions.plan_id
            WHERE payments.id = {self.store.param()} OR payments.provider_payment_id = {self.store.param()}
            """,
            (checkout_id, checkout_id),
        )
        if not row:
            return None
        return dict(row)

    def verify_checkout(
        self,
        checkout_id: str,
        *,
        status: str,
        provider_reference: str | None = None,
        raw_payload: dict[str, Any] | None = None,
        actor_principal: str | None = None,
        route: str | None = None,
        request_id: str | None = None,
        source_ip: str | None = None,
    ) -> dict[str, Any]:
        checkout = self.get_checkout(checkout_id)
        if not checkout:
            raise ValueError("Checkout not found.")
        normalized = str(status or "").strip().lower()
        if not normalized:
            normalized = "pending"
        now = iso_now()
        raw_json = json.dumps(raw_payload or {"status": status}, separators=(",", ":"))
        payment_status = "completed" if normalized in ACTIVE_PAYMENT_STATUSES else normalized
        if normalized in FAILED_PAYMENT_STATUSES:
            payment_status = "failed"
        self.store.execute(
            f"""
            UPDATE payments
            SET status = {self.store.param()},
                provider_reference = COALESCE({self.store.param()}, provider_reference),
                verified_at = CASE WHEN {self.store.param()} = 'completed' THEN {self.store.param()} ELSE verified_at END,
                raw_payload_json = {self.store.param()},
                updated_at = {self.store.param()}
            WHERE id = {self.store.param()}
            """,
            (payment_status, provider_reference, payment_status, now, raw_json, now, checkout["id"]),
        )
        if payment_status == "completed":
            self._activate_subscription(checkout["subscription_id"], checkout["invoice_id"])
        elif payment_status == "failed":
            self.store.execute(
                f"UPDATE invoices SET status = 'failed', updated_at = {self.store.param()} WHERE id = {self.store.param()}",
                (now, checkout["invoice_id"]),
            )
        after = self.get_checkout(checkout["id"]) or {}
        self.record_audit_event(
            action="checkout.verify",
            actor_principal=actor_principal,
            route=route,
            object_type="checkout",
            object_id=str(checkout["id"]),
            before=checkout,
            after=after,
            request_id=request_id,
            source_ip=source_ip,
            metadata={"provider_reference": provider_reference, "status": status},
        )
        return after

    def _activate_subscription(self, subscription_id: str, invoice_id: str) -> None:
        now_dt = utc_now()
        now = now_dt.isoformat()
        renews_at = (now_dt + timedelta(days=30)).isoformat()
        self.store.execute(
            f"""
            UPDATE subscriptions
            SET status = 'active', starts_at = COALESCE(starts_at, {self.store.param()}),
                renews_at = {self.store.param()}, updated_at = {self.store.param()}
            WHERE id = {self.store.param()} AND status != 'active'
            """,
            (now, renews_at, now, subscription_id),
        )
        self.store.execute(
            f"""
            UPDATE invoices SET status = 'paid', paid_at = COALESCE(paid_at, {self.store.param()}),
                updated_at = {self.store.param()} WHERE id = {self.store.param()}
            """,
            (now, now, invoice_id),
        )

    def create_api_key_for_checkout(
        self,
        checkout_id: str,
        *,
        claim_token: str | None = None,
        name: str | None = None,
        actor_principal: str | None = None,
        route: str | None = None,
        request_id: str | None = None,
        source_ip: str | None = None,
    ) -> dict[str, Any]:
        checkout = self.get_checkout(checkout_id)
        if not checkout:
            raise ValueError("Checkout not found.")
        expected_claim_token = self._claim_token_for_checkout(str(checkout["id"]))
        if not claim_token or not hmac.compare_digest(
            claim_token,
            expected_claim_token,
        ):
            raise BillingAuthError(403, "Valid checkout claim token required.")
        if checkout["subscription_status"] != "active":
            raise BillingAuthError(403, "Subscription is not active yet.")
        existing = self.store.fetchone(
            f"""
            SELECT id, key_prefix, tier, active, created_at
            FROM api_keys
            WHERE subscription_id = {self.store.param()} AND {self._active_sql()}
            ORDER BY created_at ASC
            LIMIT 1
            """,
            (checkout["subscription_id"],),
        )
        if existing:
            return {
                "api_key": None,
                "key": existing,
                "message": "An active key already exists. For security, the full key cannot be shown again.",
            }

        full_key, key_prefix, secret = generate_api_key()
        key_hash = hash_api_key_secret(secret, self.settings.api_key_pepper)
        now = iso_now()
        key_id = _new_id("key")
        self.store.execute(
            f"""
            INSERT INTO api_keys (id, customer_id, subscription_id, key_prefix, key_hash, name, tier, monthly_limit, active, created_at)
            VALUES ({self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()})
            """,
            (
                key_id,
                checkout["customer_id"],
                checkout["subscription_id"],
                key_prefix,
                key_hash,
                name or f"{checkout['tier']} key",
                checkout["tier"],
                checkout["monthly_limit"],
                True,
                now,
            ),
        )
        public_key_record = {
            "id": key_id,
            "key_prefix": key_prefix,
            "tier": checkout["tier"],
            "monthly_limit": checkout["monthly_limit"],
            "created_at": now,
        }
        self.record_audit_event(
            action="api_key.create",
            actor_principal=actor_principal or f"checkout:{checkout['id']}",
            route=route,
            object_type="api_key",
            object_id=key_id,
            before=None,
            after=public_key_record,
            request_id=request_id,
            source_ip=source_ip,
            metadata={
                "checkout_id": checkout["id"],
                "key_prefix": key_prefix,
                "claim_token_used": bool(claim_token),
            },
        )
        return {
            "api_key": full_key,
            "key": public_key_record,
            "message": "Store this key now. Parva only shows the full secret once.",
        }

    def authenticate_api_key(self, raw_key: str) -> dict[str, Any]:
        parsed = parse_api_key(raw_key)
        if not parsed:
            raise BillingAuthError(401, "Invalid API key.")
        row = self.store.fetchone(
            f"""
            SELECT api_keys.*, subscriptions.status AS subscription_status,
                   subscriptions.ends_at, subscriptions.renews_at,
                   customers.email, plans.slug AS plan_slug
            FROM api_keys
            JOIN customers ON customers.id = api_keys.customer_id
            LEFT JOIN subscriptions ON subscriptions.id = api_keys.subscription_id
            LEFT JOIN plans ON plans.id = subscriptions.plan_id
            WHERE api_keys.key_prefix = {self.store.param()}
            """,
            (parsed.key_prefix,),
        )
        if not row or not verify_api_key_secret(
            parsed.secret,
            self.settings.api_key_pepper,
            row["key_hash"],
        ):
            raise BillingAuthError(401, "Invalid API key.")
        if not _bool(row["active"]) or row["revoked_at"]:
            raise BillingAuthError(403, "API key is inactive or revoked.")
        if row["subscription_status"] != "active":
            raise BillingAuthError(403, "Subscription is not active.")
        self.store.execute(
            f"UPDATE api_keys SET last_used_at = {self.store.param()} WHERE id = {self.store.param()}",
            (iso_now(), row["id"]),
        )
        return row

    def check_quota(
        self,
        *,
        subject_type: str,
        subject_id: str,
        tier: str,
        limit: int,
        bucket: str,
    ) -> QuotaDecision:
        if bucket == "monthly":
            period, reset_at = month_period()
        else:
            period, reset_at = day_period()
        placeholder = self.store.param()
        existing = self.store.fetchone(
            f"""
            SELECT count FROM usage_counters
            WHERE subject_type = {placeholder} AND subject_id = {placeholder}
              AND period = {placeholder} AND bucket = {placeholder}
            """,
            (subject_type, subject_id, period, bucket),
        )
        current = int(existing["count"]) if existing else 0
        if current >= limit:
            return QuotaDecision(
                allowed=False,
                limit=limit,
                remaining=0,
                reset_at=reset_at,
                tier=tier,
                detail=f"{tier.title()} quota exceeded. Upgrade or wait until reset.",
            )
        if existing:
            self.store.execute(
                f"""
                UPDATE usage_counters SET count = count + 1, reset_at = {placeholder}
                WHERE subject_type = {placeholder} AND subject_id = {placeholder}
                  AND period = {placeholder} AND bucket = {placeholder}
                """,
                (reset_at, subject_type, subject_id, period, bucket),
            )
        else:
            self.store.execute(
                f"""
                INSERT INTO usage_counters (subject_type, subject_id, period, bucket, count, reset_at)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, 1, {placeholder})
                """,
                (subject_type, subject_id, period, bucket, reset_at),
            )
        return QuotaDecision(
            allowed=True,
            limit=limit,
            remaining=max(limit - current - 1, 0),
            reset_at=reset_at,
            tier=tier,
        )

    def usage_for_subject(self, *, subject_type: str, subject_id: str, bucket: str, limit: int, tier: str) -> dict[str, Any]:
        period, reset_at = month_period() if bucket == "monthly" else day_period()
        row = self.store.fetchone(
            f"""
            SELECT count, reset_at FROM usage_counters
            WHERE subject_type = {self.store.param()} AND subject_id = {self.store.param()}
              AND period = {self.store.param()} AND bucket = {self.store.param()}
            """,
            (subject_type, subject_id, period, bucket),
        )
        used = int(row["count"]) if row else 0
        return {
            "subject_type": subject_type,
            "subject_id": subject_id,
            "tier": tier,
            "bucket": bucket,
            "period": period,
            "limit": limit,
            "used": used,
            "remaining": max(limit - used, 0),
            "reset_at": row["reset_at"] if row else reset_at,
        }

    def revoke_key(
        self,
        key_id: str,
        *,
        actor_principal: str | None = None,
        route: str | None = None,
        request_id: str | None = None,
        source_ip: str | None = None,
    ) -> dict[str, Any]:
        before = self.store.fetchone(
            f"SELECT id, key_prefix, tier, active, revoked_at FROM api_keys WHERE id = {self.store.param()}",
            (key_id,),
        )
        now = iso_now()
        self.store.execute(
            f"UPDATE api_keys SET active = {self.store.param()}, revoked_at = {self.store.param()} WHERE id = {self.store.param()}",
            (False, now, key_id),
        )
        row = self.store.fetchone(f"SELECT id, key_prefix, tier, active, revoked_at FROM api_keys WHERE id = {self.store.param()}", (key_id,))
        if not row:
            raise ValueError("API key not found.")
        self.record_audit_event(
            action="api_key.revoke",
            actor_principal=actor_principal,
            route=route,
            object_type="api_key",
            object_id=key_id,
            before=before,
            after=row,
            request_id=request_id,
            source_ip=source_ip,
        )
        return row

    def create_webhook_subscription(self, *, api_key_id: str, customer_id: str, url: str, event_types: list[str], secret: str) -> dict[str, Any]:
        webhook_id = _new_id("wh")
        now = iso_now()
        secret_hash = hash_api_key_secret(secret, self.settings.api_key_pepper)
        self.store.execute(
            f"""
            INSERT INTO webhook_subscriptions (id, customer_id, api_key_id, url, secret_hash, event_types, active, created_at)
            VALUES ({self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()}, {self.store.param()})
            """,
            (webhook_id, customer_id, api_key_id, url, secret_hash, json.dumps(event_types), True, now),
        )
        return {
            "id": webhook_id,
            "url": url,
            "event_types": event_types,
            "signing_secret": secret,
            "created_at": now,
        }

    def admin_customers(self) -> list[dict[str, Any]]:
        return self.store.fetchall(
            """
            SELECT customers.*, COUNT(api_keys.id) AS api_key_count
            FROM customers
            LEFT JOIN api_keys ON api_keys.customer_id = customers.id
            GROUP BY customers.id
            ORDER BY customers.created_at DESC
            LIMIT 200
            """
        )

    def admin_subscriptions(self) -> list[dict[str, Any]]:
        return self.store.fetchall(
            """
            SELECT subscriptions.*, customers.email, plans.slug AS tier, plans.name AS plan_name
            FROM subscriptions
            JOIN customers ON customers.id = subscriptions.customer_id
            JOIN plans ON plans.id = subscriptions.plan_id
            ORDER BY subscriptions.created_at DESC
            LIMIT 200
            """
        )

    def mark_invoice_paid(
        self,
        invoice_id: str,
        *,
        provider_reference: str | None,
        notes: str | None,
        actor_principal: str | None = None,
        route: str | None = None,
        request_id: str | None = None,
        source_ip: str | None = None,
    ) -> dict[str, Any]:
        row = self.store.fetchone(f"SELECT * FROM invoices WHERE id = {self.store.param()}", (invoice_id,))
        if not row:
            raise ValueError("Invoice not found.")
        now = iso_now()
        self.store.execute(
            f"""
            UPDATE invoices SET status = 'paid', paid_at = COALESCE(paid_at, {self.store.param()}),
                notes = {self.store.param()}, updated_at = {self.store.param()}
            WHERE id = {self.store.param()}
            """,
            (now, notes, now, invoice_id),
        )
        if row["payment_id"]:
            self.store.execute(
                f"""
                UPDATE payments SET status = 'completed', provider_reference = COALESCE({self.store.param()}, provider_reference),
                    verified_at = COALESCE(verified_at, {self.store.param()}), updated_at = {self.store.param()}
                WHERE id = {self.store.param()}
                """,
                (provider_reference, now, now, row["payment_id"]),
            )
        if row["subscription_id"]:
            self._activate_subscription(row["subscription_id"], invoice_id)
        after = self.store.fetchone(f"SELECT * FROM invoices WHERE id = {self.store.param()}", (invoice_id,)) or {}
        self.record_audit_event(
            action="invoice.mark_paid",
            actor_principal=actor_principal,
            route=route,
            object_type="invoice",
            object_id=invoice_id,
            before=row,
            after=after,
            request_id=request_id,
            source_ip=source_ip,
            metadata={"provider_reference": provider_reference},
        )
        return after

    def extend_subscription(
        self,
        subscription_id: str,
        *,
        days: int = 30,
        actor_principal: str | None = None,
        route: str | None = None,
        request_id: str | None = None,
        source_ip: str | None = None,
    ) -> dict[str, Any]:
        subscription = self.store.fetchone(f"SELECT * FROM subscriptions WHERE id = {self.store.param()}", (subscription_id,))
        if not subscription:
            raise ValueError("Subscription not found.")
        now_dt = utc_now()
        current_renews = subscription.get("renews_at")
        base = now_dt
        if current_renews:
            try:
                base = max(now_dt, utc_now().fromisoformat(current_renews))
            except (TypeError, ValueError):
                base = now_dt
        renews_at = (base + timedelta(days=max(1, min(days, 366)))).isoformat()
        self.store.execute(
            f"""
            UPDATE subscriptions SET status = 'active', renews_at = {self.store.param()},
                updated_at = {self.store.param()} WHERE id = {self.store.param()}
            """,
            (renews_at, iso_now(), subscription_id),
        )
        after = self.store.fetchone(f"SELECT * FROM subscriptions WHERE id = {self.store.param()}", (subscription_id,)) or {}
        self.record_audit_event(
            action="subscription.extend",
            actor_principal=actor_principal,
            route=route,
            object_type="subscription",
            object_id=subscription_id,
            before=subscription,
            after=after,
            request_id=request_id,
            source_ip=source_ip,
            metadata={"days": days},
        )
        return after

    def usage_anomalies(self) -> list[dict[str, Any]]:
        return self.store.fetchall(
            """
            SELECT subject_type, subject_id, bucket, period, count, reset_at
            FROM usage_counters
            WHERE count >= 80
            ORDER BY count DESC
            LIMIT 100
            """
        )


_SERVICE_CACHE: dict[tuple[str, str], BillingService] = {}


def get_billing_service(settings: Any) -> BillingService:
    if not settings.billing_enabled:
        raise RuntimeError("Billing is disabled.")
    key = (settings.database_url or "", settings.api_key_pepper)
    service = _SERVICE_CACHE.get(key)
    if service is None:
        service = BillingService(settings)
        _SERVICE_CACHE[key] = service
    return service


def reset_billing_service_cache() -> None:
    _SERVICE_CACHE.clear()
