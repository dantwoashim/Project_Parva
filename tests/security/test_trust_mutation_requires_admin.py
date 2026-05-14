from __future__ import annotations

import inspect

from app.api import trust_routes
from app.services import trust_infrastructure_service


def test_trust_post_routes_are_public_evidence_builders_only():
    post_paths = sorted(
        route.path
        for route in trust_routes.router.routes
        if "POST" in getattr(route, "methods", set())
    )

    assert post_paths == [
        "/api/trust/evidence/compliance-decision",
        "/api/trust/evidence/date-conversion",
        "/api/trust/evidence/rule-execution",
    ]


def test_trust_evidence_builder_is_non_persistent():
    source = inspect.getsource(trust_infrastructure_service.build_evidence_packet)

    assert ".write" not in source
    assert "open(" not in source
