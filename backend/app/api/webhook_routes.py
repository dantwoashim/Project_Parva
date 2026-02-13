"""Webhook subscription endpoints."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.integrations import get_webhook_service


router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
_service = get_webhook_service()


class WebhookSubscriptionCreate(BaseModel):
    subscriber_url: str
    festivals: list[str] = Field(default_factory=list)
    remind_days_before: list[int] = Field(default_factory=lambda: [0])
    format: str = "json"
    active: bool = True


@router.get("")
async def list_subscriptions():
    items = _service.list_subscriptions()
    return {
        "count": len(items),
        "subscriptions": items,
    }


@router.post("/subscribe")
async def create_subscription(payload: WebhookSubscriptionCreate):
    try:
        row = _service.create_subscription(
            subscriber_url=payload.subscriber_url,
            festivals=payload.festivals,
            remind_days_before=payload.remind_days_before,
            payload_format=payload.format,
            active=payload.active,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "subscribed",
        "subscription": row,
    }


@router.get("/{subscription_id}")
async def get_subscription(subscription_id: str):
    row = _service.get_subscription(subscription_id)
    if not row:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return row


@router.delete("/{subscription_id}")
async def delete_subscription(subscription_id: str):
    ok = _service.delete_subscription(subscription_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"status": "deleted", "subscription_id": subscription_id}


@router.post("/dispatch")
async def dispatch_webhooks(
    target_date: Optional[date] = Query(None, alias="date", description="Dispatch date YYYY-MM-DD"),
    dry_run: bool = Query(False),
):
    run_date = target_date or date.today()
    result = await _service.dispatch_for_date(run_date, dry_run=dry_run)
    return result
