"""Latent truth model over fused month-start candidates."""

from __future__ import annotations

from typing import Any

from .weak_label_fusion import fuse_month_start_candidates

PUBLICATION_STATUS = "computed_prediction_not_official"


def infer_latent_truth(fusion: dict[str, Any] | None = None) -> dict[str, Any]:
    fusion = fusion or fuse_month_start_candidates()
    results = {}
    review_cases = []
    for key, item in fusion.get("results", {}).items():
        candidates = item.get("posterior_candidates", [])
        selected = candidates[0] if candidates else {}
        truth_probability = float(selected.get("posterior_probability") or 0.0)
        review_required = bool(item.get("conflict")) or truth_probability < 0.75
        if review_required:
            review_cases.append(key)
        results[key] = {
            "bs_year": item["bs_year"],
            "bs_month": item["bs_month"],
            "latent_truth_month_start_ad": selected.get("month_start_ad", item.get("selected_month_start_ad")),
            "truth_probability": round(truth_probability, 6),
            "manual_review_required": review_required,
            "reason": "low_margin_or_source_conflict" if review_required else "source_weighted_consensus",
            "candidate_count": len(candidates),
        }
    return {
        "publication_status": PUBLICATION_STATUS,
        "method": "reliability_weighted_latent_truth_v1",
        "case_count": len(results),
        "manual_review_required_count": len(review_cases),
        "manual_review_cases": review_cases[:200],
        "results": results,
    }
