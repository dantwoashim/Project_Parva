"""Compliance report renderer."""

from __future__ import annotations


def render_obligation_report(flow: dict) -> str:
    obligation = flow["obligation"]
    return (
        "# Sample Obligation Report\n\n"
        "This fictional sample is planning/review support, not legal or tax authority.\n\n"
        f"- Source: `{obligation['source_docket_id']}`\n"
        f"- Extraction: `{flow['extraction_receipt']['receipt_id']}`\n"
        f"- Effective date: `{obligation['effective_bs']}`\n"
        f"- Deadline: `{obligation['deadline_bs']}`\n"
        f"- Required action: {obligation['required_action']}\n"
        f"- Applicability: `{obligation['applicability']['entity_type']}`\n"
        f"- Boundary: `{obligation['boundary']['claim_boundary']}`\n"
    )
