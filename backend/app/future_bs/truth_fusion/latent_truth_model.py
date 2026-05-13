"""Backward-compatible wrapper for the consensus truth selector.

The historical function name is kept for imports and artifact compatibility,
but the returned metadata is explicit that this is reliability-weighted
consensus selection, not a full Bayesian latent-variable model.
"""

from __future__ import annotations

from typing import Any

from .consensus_truth_selector import infer_consensus_truth


def infer_latent_truth(fusion: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = infer_consensus_truth(fusion)
    for item in payload["results"].values():
        item["latent_truth_month_start_ad"] = item["selected_month_start_ad"]
        item["truth_probability"] = item["consensus_probability"]
    payload["compatibility_name"] = "infer_latent_truth"
    return payload
