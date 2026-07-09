"""Copy/dependence report generation for source witnesses."""

from __future__ import annotations

from typing import Any

from .source_independence import build_source_independence_graph

PUBLICATION_STATUS = "computed_prediction_not_official"


def detect_source_copy_patterns(graph: dict[str, Any] | None = None) -> dict[str, Any]:
    graph = graph or build_source_independence_graph()
    high_risk = [edge for edge in graph.get("edges", []) if edge.get("copy_risk")]
    identical = [edge for edge in high_risk if edge.get("agreement_jaccard") == 1.0]
    return {
        "publication_status": PUBLICATION_STATUS,
        "copy_risk_edges": len(high_risk),
        "identical_table_like_edges": len(identical),
        "high_risk_pairs": high_risk[:200],
        "confidence_policy": "Copy-risk sources are down-weighted for weak fusion and cannot independently promote official_strict claim-readiness.",
    }
