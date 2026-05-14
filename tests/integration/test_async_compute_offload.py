from __future__ import annotations

import asyncio
import time

import httpx
from app.bootstrap.app_factory import create_app


async def _async_client(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


def test_slow_muhurta_compute_does_not_block_health_route(monkeypatch):
    import app.api.muhurta_routes as muhurta_routes

    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")

    def slow_muhurta(**_kwargs):
        time.sleep(0.25)
        return {"ok": True, "route": "muhurta"}

    monkeypatch.setattr(muhurta_routes, "build_muhurta_for_day_response", slow_muhurta)
    app = create_app()

    async def run_case():
        async with await _async_client(app) as client:
            compute_task = asyncio.create_task(
                client.get("/v3/api/muhurta", params={"date": "2026-04-14"})
            )
            await asyncio.sleep(0.05)
            started = time.perf_counter()
            health = await client.get("/health/live")
            latency = time.perf_counter() - started
            compute = await compute_task
        return health, latency, compute

    health, latency, compute = asyncio.run(run_case())

    assert health.status_code == 200
    assert latency < 0.20
    assert compute.status_code == 200
    assert compute.json()["ok"] is True
