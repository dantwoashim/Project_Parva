from __future__ import annotations

import asyncio
import time

import httpx
from app.billing import reset_billing_service_cache
from app.billing.service import BillingService
from app.bootstrap.app_factory import create_app


async def _async_client(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


def test_slow_billing_call_does_not_block_health_route(monkeypatch):
    reset_billing_service_cache()
    monkeypatch.setenv("PARVA_BILLING_ENABLED", "true")
    monkeypatch.setenv("PARVA_DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("PARVA_API_KEY_PEPPER", "test-pepper")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")

    original = BillingService.create_checkout

    def slow_create_checkout(self, **kwargs):
        time.sleep(0.25)
        return original(self, **kwargs)

    monkeypatch.setattr(BillingService, "create_checkout", slow_create_checkout)
    app = create_app()

    async def run_case():
        async with await _async_client(app) as client:
            checkout_task = asyncio.create_task(
                client.post(
                    "/v3/api/billing/checkout",
                    json={
                        "email": "slow@example.com",
                        "tier": "starter",
                        "provider": "manual_bank_qr",
                    },
                )
            )
            await asyncio.sleep(0.05)
            started = time.perf_counter()
            health = await client.get("/health/live")
            latency = time.perf_counter() - started
            checkout = await checkout_task
        return health, latency, checkout

    health, latency, checkout = asyncio.run(run_case())

    assert health.status_code == 200
    assert latency < 0.20
    assert checkout.status_code == 200
