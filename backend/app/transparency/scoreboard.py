"""Forecast scoreboard records."""

from __future__ import annotations


def resolve_forecast(commitment: dict, resolution: dict) -> dict:
    return {
        "commitment": commitment,
        "resolution": resolution,
        "status": "resolved",
        "official_authority": False,
    }
