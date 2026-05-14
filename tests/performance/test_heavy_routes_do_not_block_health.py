from __future__ import annotations

import asyncio
import time

import httpx
from app.bootstrap.app_factory import create_app


async def _async_client(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


def test_slow_kundali_compute_does_not_block_health_route(monkeypatch):
    import app.api.kundali_routes as kundali_routes

    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "developer_preview")

    def slow_kundali(**_kwargs):
        time.sleep(0.25)
        return {"ok": True, "route": "kundali"}

    monkeypatch.setattr(kundali_routes, "_build_kundali_response", slow_kundali)
    app = create_app()

    async def run_case():
        async with await _async_client(app) as client:
            compute_task = asyncio.create_task(
                client.get("/v3/api/kundali", params={"datetime": "2026-04-14T09:00:00"})
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
