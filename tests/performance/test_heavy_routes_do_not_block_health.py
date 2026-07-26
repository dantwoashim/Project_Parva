from __future__ import annotations

import asyncio
from threading import Event

import httpx
from app.bootstrap.app_factory import create_app


async def _async_client(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


def test_slow_kundali_compute_does_not_block_health_route(monkeypatch):
    import app.api.kundali_routes as kundali_routes

    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "developer_preview")

    compute_started = Event()
    compute_release = Event()

    def slow_kundali(**_kwargs):
        compute_started.set()
        assert compute_release.wait(2.0), "Kundali worker was not released"
        return {"ok": True, "route": "kundali"}

    monkeypatch.setattr(kundali_routes, "_build_kundali_response", slow_kundali)
    app = create_app()

    async def run_case():
        async with await _async_client(app) as client:
            compute_task = asyncio.create_task(
                client.get("/v3/api/kundali", params={"datetime": "2026-04-14T09:00:00"})
            )
            for _ in range(100):
                if compute_started.is_set():
                    break
                await asyncio.sleep(0.005)
            assert compute_started.is_set(), "Kundali computation did not enter the worker thread"
            try:
                health = await asyncio.wait_for(client.get("/health/live"), timeout=1.0)
                compute_was_pending = not compute_task.done()
            finally:
                compute_release.set()
            compute = await asyncio.wait_for(compute_task, timeout=2.0)
        return health, compute_was_pending, compute

    health, compute_was_pending, compute = asyncio.run(run_case())

    assert health.status_code == 200
    assert compute_was_pending is True
    assert compute.status_code == 200
    assert compute.json()["ok"] is True
