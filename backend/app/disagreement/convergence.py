"""Branch convergence analysis."""

from __future__ import annotations


def convergence_report(branches: list[dict]) -> dict:
    values = [branch.get("result") for branch in branches]
    return {
        "all_agree": all(value == values[0] for value in values) if values else True,
        "branch_count": len(branches),
        "conflict_status": "converged" if len(set(map(str, values))) <= 1 else "conflicted",
    }
