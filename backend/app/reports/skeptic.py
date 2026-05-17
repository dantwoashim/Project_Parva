"""Skeptic report renderer."""

from __future__ import annotations

from app.disagreement.convergence import convergence_report


def render_skeptic_report(branches: list[dict]) -> str:
    report = convergence_report(branches)
    lines = [
        "# Skeptic Report",
        "",
        f"Conflict status: `{report['conflict_status']}`",
        "",
        "Branches:",
    ]
    for branch in branches:
        lines.append(f"- `{branch['branch_id']}`: {branch['result']} ({branch['boundary']['authority']})")
    return "\n".join(lines) + "\n"
