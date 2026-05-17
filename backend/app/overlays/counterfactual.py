"""Counterfactual membrane generation."""

from __future__ import annotations

from app.overlays.pack import apply_overlay


def counterfactual_membrane(baseline: dict, overlay: dict) -> dict:
    changed = apply_overlay(baseline, overlay)
    return {
        "kind": "parva_membrane",
        "membrane_kind": "counterfactual",
        "baseline": baseline,
        "overlay": overlay,
        "changed": changed,
        "changed_dates": {
            "before": baseline.get("selected_days"),
            "after": changed.get("selected_days"),
        },
        "reason": "overlay_pack_applied_without_mutating_baseline",
    }
