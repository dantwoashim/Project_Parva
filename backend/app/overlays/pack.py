"""Overlay pack schema."""

from __future__ import annotations


def apply_overlay(schedule: dict, overlay: dict) -> dict:
    changed = dict(schedule)
    if "remove_days" in overlay and "selected_days" in changed:
        changed["selected_days"] = [day for day in changed["selected_days"] if day not in set(overlay["remove_days"])]
    changed["overlay_applied"] = overlay.get("overlay_id", "overlay")
    return changed
