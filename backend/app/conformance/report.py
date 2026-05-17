"""Render conformance reports."""

from __future__ import annotations


def render_conformance_report(result: dict) -> str:
    lines = [
        "# Payroll Date Risk Conformance Report",
        "",
        f"Capsule: `{result['capsule_id']}`",
        "",
        "This is a technical conformance report, not certification or legal/tax/payroll authority.",
        "",
    ]
    for item in result["results"]:
        lines.append(f"- `{item['bs_date']}`: {item['status']} - {', '.join(item['issues']) or 'no issues'}")
    return "\n".join(lines) + "\n"
