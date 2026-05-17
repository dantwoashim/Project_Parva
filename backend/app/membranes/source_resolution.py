"""Membrane-facing source resolution helpers."""

from __future__ import annotations

from app.sources.coverage import SourceCoverageResolution, resolve_bs_date_source


def resolve_convert_bs_to_ad_source(year: int, month: int, day: int) -> SourceCoverageResolution:
    return resolve_bs_date_source("convert_bs_to_ad", year=year, month=month, day=day)


__all__ = ["resolve_convert_bs_to_ad_source"]
