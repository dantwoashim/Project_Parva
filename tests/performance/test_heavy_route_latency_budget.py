from __future__ import annotations

from pathlib import Path

HEAVY_ROUTE_MODULES = [
    "backend/app/api/agent_routes.py",
    "backend/app/api/future_bs_routes.py",
    "backend/app/api/impact_routes.py",
    "backend/app/api/kundali_graph_routes.py",
    "backend/app/api/kundali_routes.py",
    "backend/app/api/muhurta_calendar_routes.py",
    "backend/app/api/muhurta_heatmap_routes.py",
    "backend/app/api/muhurta_routes.py",
    "backend/app/api/observance_routes.py",
    "backend/app/api/personal_routes.py",
    "backend/app/api/public_demo_routes.py",
    "backend/app/api/rules_routes.py",
    "backend/app/api/timegraph_routes.py",
    "backend/app/calendar/routes.py",
]


def test_heavy_async_route_modules_use_threadpool_offload():
    root = Path(__file__).resolve().parents[2]
    missing = [
        module
        for module in HEAVY_ROUTE_MODULES
        if "run_cpu_bound" not in (root / module).read_text(encoding="utf-8")
    ]

    assert missing == []
