"""Performance gates for cached future-BS prediction paths."""

from __future__ import annotations

from time import perf_counter

from app.future_bs.ensemble import compute_year_live, predict_year


def test_cached_live_year_compute_is_under_300ms():
    compute_year_live(2085)

    started = perf_counter()
    compute_year_live(2085)
    elapsed_ms = (perf_counter() - started) * 1000

    assert elapsed_ms < 300


def test_precomputed_api_path_is_under_50ms():
    predict_year(2085)

    started = perf_counter()
    predict_year(2085)
    elapsed_ms = (perf_counter() - started) * 1000

    assert elapsed_ms < 50
