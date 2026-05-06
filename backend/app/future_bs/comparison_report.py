"""Comparison report helpers."""

from __future__ import annotations

from typing import Any


def comparison_report_markdown(comparison: dict[str, Any]) -> str:
    lines = [
        "# Future BS Month-Length Comparison Report",
        "",
        f"Source: {comparison['source_name']}",
        f"Years compared: {comparison['summary']['years_compared']}",
        f"Months compared: {comparison['summary']['months_compared']}",
        f"Matches: {comparison['summary']['matches']}",
        f"Mismatches: {comparison['summary']['mismatches']}",
        f"Match rate: {comparison['summary']['match_rate']}%",
        "",
        "## Mismatches",
    ]
    if not comparison["mismatches"]:
        lines.append("No mismatches.")
    for row in comparison["mismatches"]:
        lines.append(
            f"- {row['bs_year']} {row['month_name']}: source={row['their_days']}, "
            f"parva={row['parva_days']}, confidence={row['confidence']}, "
            f"recommendation={row['recommendation']}"
        )
    return "\n".join(lines) + "\n"
