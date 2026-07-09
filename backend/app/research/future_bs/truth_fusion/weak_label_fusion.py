"""Weak-label fusion over source-agreement candidates."""

from __future__ import annotations

import json
from typing import Any

from app.research.future_bs.paths import project_root

from .source_reliability import reliability_for_source_type

PROJECT_ROOT = project_root()
GRAPH_PATH = PROJECT_ROOT / "data" / "future_bs" / "corpus" / "source_agreement_graph.json"
PUBLICATION_STATUS = "computed_prediction_not_official"


def _source_type_from_id(source_id: str) -> str:
    source_id = source_id.lower()
    if "official" in source_id:
        return "official_verified"
    if "patro" in source_id or "panchanga" in source_id:
        return "printed_verified"
    if "rat32" in source_id or "ratopati" in source_id:
        return "publisher_reference"
    if "medic" in source_id or "sharingapples" in source_id:
        return "software_table_reference"
    if "hamropatro" in source_id:
        return "third_party_reference"
    return "needs_review"


def fuse_month_start_candidates(graph: dict[str, Any] | None = None) -> dict[str, Any]:
    if graph is None:
        if not GRAPH_PATH.exists():
            return {
                "publication_status": PUBLICATION_STATUS,
                "method": "source_reliability_weighted_candidate_fusion",
                "case_count": 0,
                "low_margin_count": 0,
                "low_margin_cases": [],
                "results": {},
                "artifact_status": "source_agreement_graph_not_present",
            }
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    results = {}
    low_margin = []
    for key, node in graph.get("nodes", {}).items():
        weighted = []
        total = 0.0
        for candidate in node.get("candidates", []):
            source_ids = candidate.get("source_ids") or []
            source_weight = sum(reliability_for_source_type(_source_type_from_id(str(source))) for source in source_ids)
            score = float(candidate.get("weight") or 0.0) + source_weight
            total += score
            weighted.append({**candidate, "fusion_score": round(score, 6)})
        posterior = []
        for candidate in weighted:
            prob = float(candidate["fusion_score"]) / total if total else 0.0
            posterior.append({**candidate, "posterior_probability": round(prob, 6)})
        posterior.sort(key=lambda row: row["posterior_probability"], reverse=True)
        margin = 1.0
        if len(posterior) > 1:
            margin = posterior[0]["posterior_probability"] - posterior[1]["posterior_probability"]
        if margin < 0.25 or node.get("conflict"):
            low_margin.append(key)
        results[key] = {
            "bs_year": node["bs_year"],
            "bs_month": node["bs_month"],
            "posterior_candidates": posterior,
            "selected_month_start_ad": posterior[0]["month_start_ad"] if posterior else node.get("chosen_month_start_ad"),
            "posterior_confidence": posterior[0]["posterior_probability"] if posterior else 0.0,
            "low_margin": margin < 0.25,
            "conflict": bool(node.get("conflict")),
        }
    return {
        "publication_status": PUBLICATION_STATUS,
        "method": "source_reliability_weighted_candidate_fusion",
        "case_count": len(results),
        "low_margin_count": len(low_margin),
        "low_margin_cases": low_margin[:200],
        "results": results,
    }
