"""Billing, API key, usage, webhook, and admin endpoints."""

from __future__ import annotations

import json
import logging
import math
import secrets
from asyncio import to_thread
from datetime import datetime, timezone
from ipaddress import ip_address
from typing import Any, Literal
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.billing import BillingAuthError, get_billing_service
from app.billing.plans import FREE_DAILY_LIMIT, FREE_MONTHLY_LIMIT
from app.security.pii import scrub_structured_trace

router = APIRouter(prefix="/api", tags=["billing"])
audit_logger = logging.getLogger("parva.billing.audit")


class CheckoutRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    tier: Literal["starter", "professional", "enterprise"]
    provider: Literal[
        "manual_qr",
        "manual_bank_qr",
        "manual_esewa_qr",
        "manual_khalti_qr",
        "manual_contact",
        "payoneer",
        "khalti",
        "esewa",
    ] = "manual_bank_qr"
    name: str | None = Field(default=None, max_length=160)
    company_name: str | None = Field(default=None, max_length=180)
    country: str | None = Field(default="NP", max_length=80)
    phone: str | None = Field(default=None, max_length=80)


class VerifyCheckoutRequest(BaseModel):
    status: str = Field(min_length=1, max_length=80)
    provider_reference: str | None = Field(default=None, max_length=180)
    provider: Literal["manual", "khalti", "esewa", "payoneer"] = "manual"
    raw_payload: dict[str, Any] | None = None

    @field_validator("raw_payload")
    @classmethod
    def _validate_raw_payload(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
        if len(encoded.encode("utf-8")) > 4096:
            raise ValueError("raw_payload must be 4096 bytes or smaller")

        def walk(node: Any, *, depth: int) -> None:
            if depth > 5:
                raise ValueError("raw_payload nesting depth must be 5 or less")
            if isinstance(node, dict):
                if len(node) > 40:
                    raise ValueError("raw_payload objects may contain at most 40 keys")
                for key, child in node.items():
                    if not isinstance(key, str) or len(key) > 120:
                        raise ValueError("raw_payload keys must be strings up to 120 characters")
                    walk(child, depth=depth + 1)
            elif isinstance(node, list):
                if len(node) > 40:
                    raise ValueError("raw_payload arrays may contain at most 40 items")
                for child in node:
                    walk(child, depth=depth + 1)
            elif isinstance(node, float) and not math.isfinite(node):
                raise ValueError("raw_payload numbers must be finite")
            elif not isinstance(node, (str, int, float, bool, type(None))):
                raise ValueError("raw_payload values must be JSON primitives, arrays, or objects")

        walk(value, depth=0)
        return value


class CreateKeyRequest(BaseModel):
    checkout_id: str
    claim_token: str | None = Field(default=None, min_length=32, max_length=160)
    name: str | None = Field(default=None, max_length=120)


class WebhookRequest(BaseModel):
    url: HttpUrl
    event_types: list[str] = Field(default_factory=lambda: ["festival.upcoming"], min_length=1, max_length=12)

    @field_validator("url")
    @classmethod
    def _reject_private_webhook_destinations(cls, value: HttpUrl) -> HttpUrl:
        host = (urlparse(str(value)).hostname or "").strip().lower()
        if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
            raise ValueError("webhook URL host must not be localhost or .local")
        try:
            address = ip_address(host)
        except ValueError:
            return value
        if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
            raise ValueError("webhook URL host must not be private, loopback, link-local, or reserved IP")
        return value

    @field_validator("event_types")
    @classmethod
    def _validate_event_types(cls, value: list[str]) -> list[str]:
        allowed = {"festival.upcoming", "calendar.release", "trust.release"}
        normalized = [item.strip() for item in value if item.strip()]
        if len(normalized) != len(set(normalized)):
            raise ValueError("event_types must not contain duplicates")
        unsupported = sorted(set(normalized) - allowed)
        if unsupported:
            raise ValueError(f"unsupported webhook event types: {', '.join(unsupported)}")
        return normalized


class MarkInvoicePaidRequest(BaseModel):
    provider_reference: str | None = Field(default=None, max_length=180)
    notes: str | None = Field(default=None, max_length=500)


class ExtendSubscriptionRequest(BaseModel):
    days: int = Field(default=30, ge=1, le=366)


def _service(request: Request):
    settings = request.app.state.settings
    if not settings.billing_enabled:
        raise HTTPException(status_code=503, detail="Billing is disabled. Set PARVA_BILLING_ENABLED=true.")
    return get_billing_service(settings)


def _principal(request: Request):
    return getattr(request.state, "principal", None)


def _require_admin(request: Request) -> None:
    principal = _principal(request)
    if getattr(principal, "principal_type", None) != "admin":
        raise HTTPException(status_code=403, detail="Admin token required.")


def _require_api_key(request: Request):
    principal = _principal(request)
    if getattr(principal, "principal_type", None) != "api_key":
        raise HTTPException(status_code=401, detail="Valid API key required.")
    return principal


def _admin_audit_event(
    request: Request,
    *,
    action_type: str,
    invoice_id: str | None = None,
    subscription_id: str | None = None,
    key_id: str | None = None,
    provider: str | None = None,
    provider_reference: str | None = None,
) -> None:
    principal = _principal(request)
    payload = scrub_structured_trace(
        {
            "event": "billing.admin_action",
            "action_type": action_type,
            "admin_principal": getattr(principal, "principal_id", None),
            "invoice_id": invoice_id,
            "subscription_id": subscription_id,
            "key_id": key_id,
            "provider": provider,
            "provider_reference": provider_reference,
            "request_id": getattr(request.state, "request_id", None),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_ip": getattr(request.state, "client_ip", None),
        }
    )
    audit_logger.info(
        json.dumps(
            payload,
            sort_keys=True,
        )
    )


def _audit_context(request: Request) -> dict[str, Any]:
    principal = _principal(request)
    return {
        "actor_principal": getattr(principal, "principal_id", None),
        "route": request.url.path,
        "request_id": getattr(request.state, "request_id", None),
        "source_ip": getattr(request.state, "client_ip", None),
    }


async def _billing_call(request: Request, method_name: str, *args, **kwargs):
    # Billing storage is intentionally synchronous today, so route handlers
    # offload service creation and DB work to keep the FastAPI event loop free.
    def _invoke():
        service = _service(request)
        method = getattr(service, method_name)
        return method(*args, **kwargs)

    return await to_thread(_invoke)


@router.get("/billing/plans")
async def billing_plans(request: Request):
    return {
        "plans": await _billing_call(request, "list_plans"),
        "free_daily_limit": FREE_DAILY_LIMIT,
        "free_monthly_limit": FREE_MONTHLY_LIMIT,
    }


@router.post("/billing/checkout")
async def create_billing_checkout(payload: CheckoutRequest, request: Request):
    try:
        checkout = await _billing_call(request, "create_checkout", **payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return checkout


@router.get("/billing/checkout/{checkout_id}")
async def get_billing_checkout(checkout_id: str, request: Request):
    checkout = await _billing_call(request, "get_checkout", checkout_id)
    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout not found.")
    return checkout


@router.post("/billing/checkout/{checkout_id}/verify")
async def verify_billing_checkout(checkout_id: str, payload: VerifyCheckoutRequest, request: Request):
    settings = request.app.state.settings
    principal = _principal(request)
    if (
        settings.environment.lower() == "production"
        and getattr(principal, "principal_type", None) != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Production payment activation requires admin confirmation.",
        )
    try:
        checkout = await _billing_call(
            request,
            "verify_checkout",
            checkout_id,
            status=payload.status,
            provider_reference=payload.provider_reference,
            raw_payload=payload.raw_payload,
            **_audit_context(request),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return checkout


@router.post("/keys")
async def create_api_key(payload: CreateKeyRequest, request: Request):
    try:
        return await _billing_call(
            request,
            "create_api_key_for_checkout",
            payload.checkout_id,
            claim_token=payload.claim_token,
            name=payload.name,
            **_audit_context(request),
        )
    except BillingAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/keys/{key_id}")
async def revoke_api_key(key_id: str, request: Request):
    principal = _principal(request)
    if getattr(principal, "principal_type", None) not in {"api_key", "admin"}:
        raise HTTPException(status_code=401, detail="Valid API key or admin token required.")
    if getattr(principal, "principal_type", None) == "api_key" and getattr(principal, "principal_id", None) != key_id:
        raise HTTPException(status_code=403, detail="API keys can only revoke themselves.")
    try:
        return await _billing_call(request, "revoke_key", key_id, **_audit_context(request))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/me/usage")
async def my_usage(request: Request):
    principal = _principal(request)
    if getattr(principal, "principal_type", None) == "api_key":
        return await _billing_call(
            request,
            "usage_for_subject",
            subject_type="api_key",
            subject_id=principal.principal_id,
            bucket="monthly",
            limit=principal.monthly_limit or 0,
            tier=principal.tier or "paid",
        )
    client_ip = getattr(request.state, "client_ip", "unknown")
    return await _billing_call(
        request,
        "usage_for_subject",
        subject_type="ip",
        subject_id=client_ip,
        bucket="daily",
        limit=FREE_DAILY_LIMIT,
        tier="free",
    )


@router.get("/webhooks", include_in_schema=False)
async def webhooks_not_public():
    raise HTTPException(status_code=404, detail="Not Found")


@router.post("/webhooks", include_in_schema=False)
async def create_webhook(payload: WebhookRequest, request: Request):
    principal = _require_api_key(request)
    if principal.tier not in {"professional", "enterprise"}:
        raise HTTPException(status_code=403, detail="Webhook notifications require Professional or Enterprise.")
    secret = f"parva_whsec_{secrets.token_urlsafe(32)}"
    return await _billing_call(
        request,
        "create_webhook_subscription",
        api_key_id=principal.principal_id,
        customer_id=principal.customer_id or "",
        url=str(payload.url),
        event_types=payload.event_types,
        secret=secret,
    )


@router.get("/admin/customers")
async def admin_customers(request: Request):
    _require_admin(request)
    return {"customers": await _billing_call(request, "admin_customers")}


@router.get("/admin/subscriptions")
async def admin_subscriptions(request: Request):
    _require_admin(request)
    return {"subscriptions": await _billing_call(request, "admin_subscriptions")}


@router.post("/admin/invoices/{invoice_id}/mark-paid")
async def admin_mark_invoice_paid(invoice_id: str, payload: MarkInvoicePaidRequest, request: Request):
    _require_admin(request)
    try:
        invoice = await _billing_call(
            request,
            "mark_invoice_paid",
            invoice_id,
            provider_reference=payload.provider_reference,
            notes=payload.notes,
            **_audit_context(request),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _admin_audit_event(
        request,
        action_type="invoice.mark_paid",
        invoice_id=invoice_id,
        provider=invoice.get("provider") if isinstance(invoice, dict) else None,
        provider_reference=payload.provider_reference,
    )
    return invoice


@router.post("/admin/subscriptions/{subscription_id}/extend")
async def admin_extend_subscription(subscription_id: str, payload: ExtendSubscriptionRequest, request: Request):
    _require_admin(request)
    try:
        subscription = await _billing_call(
            request,
            "extend_subscription",
            subscription_id,
            days=payload.days,
            **_audit_context(request),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _admin_audit_event(
        request,
        action_type="subscription.extend",
        subscription_id=subscription_id,
    )
    return subscription


@router.post("/admin/api-keys/{key_id}/revoke")
async def admin_revoke_key(key_id: str, request: Request):
    _require_admin(request)
    try:
        result = await _billing_call(request, "revoke_key", key_id, **_audit_context(request))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _admin_audit_event(request, action_type="api_key.revoke", key_id=key_id)
    return result


@router.get("/admin/usage/anomalies")
async def admin_usage_anomalies(request: Request):
    _require_admin(request)
    return {"anomalies": await _billing_call(request, "usage_anomalies")}
