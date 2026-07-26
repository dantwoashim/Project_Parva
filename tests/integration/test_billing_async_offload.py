from __future__ import annotations

import asyncio
from threading import Event

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
    checkout_started = Event()
    checkout_release = Event()

    def slow_create_checkout(self, **kwargs):
        checkout_started.set()
        assert checkout_release.wait(2.0), "Billing checkout worker was not released"
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
            for _ in range(100):
                if checkout_started.is_set():
                    break
                await asyncio.sleep(0.005)
            assert checkout_started.is_set(), "Billing checkout did not enter the worker thread"
            try:
                health = await asyncio.wait_for(client.get("/health/live"), timeout=1.0)
                checkout_was_pending = not checkout_task.done()
            finally:
                checkout_release.set()
            checkout = await asyncio.wait_for(checkout_task, timeout=2.0)
        return health, checkout_was_pending, checkout

    health, checkout_was_pending, checkout = asyncio.run(run_case())

    assert health.status_code == 200
    assert checkout_was_pending is True
    assert checkout.status_code == 200
