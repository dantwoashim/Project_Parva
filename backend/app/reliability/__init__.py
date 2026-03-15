"""Reliability helpers and SLO/status evaluators."""

from .slo import evaluate_slos


def get_runtime_status():
    from .status import get_runtime_status as _get_runtime_status

    return _get_runtime_status()

__all__ = ["evaluate_slos", "get_runtime_status"]
