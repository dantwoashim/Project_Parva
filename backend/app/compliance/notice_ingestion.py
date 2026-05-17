"""Semi-manual notice-to-obligation ingestion."""

from __future__ import annotations

from app.compliance.obligation import Obligation
from app.compliance.requirement import document_requirement
from app.membranes.capsule import build_convert_bs_to_ad_capsule


def ingest_notice(text: str) -> dict:
    if "2082-04-31" not in text:
        raise ValueError("sample notice must include deadline 2082-04-31")
    docket = {
        "source_docket_id": "parva:src:v1:sample-notice",
        "source_text_hash_boundary": "sample_public_notice_not_authority",
    }
    receipt = {
        "receipt_id": "parva:extract:v1:sample-notice-deadline",
        "extracted_deadline": "2082-04-31",
        "review_status": "review_required",
    }
    deadline_membrane = build_convert_bs_to_ad_capsule(2082, 4, 31)
    obligation = Obligation(
        obligation_id="parva:obl:v1:sample-notice-payroll",
        claim_type="deadline_claim",
        source_docket_id=docket["source_docket_id"],
        applicability={
            "entity_type": "fictional_vendor",
            "jurisdiction": "np:sample",
            "industry": "software",
            "institution": "sample",
            "role": "operator",
        },
        effective_bs="2082-04-01",
        deadline_bs="2082-04-31",
        required_action="Review payroll date handling before deadline.",
        required_documents=[document_requirement("date-risk-export")["name"]],
        boundary={"claim_boundary": "planning_support_not_legal_or_tax_authority", "review_required": True},
        proof_pack=deadline_membrane["proof_pack"],
    )
    return {
        "source_docket": docket,
        "extraction_receipt": receipt,
        "deadline_membrane": deadline_membrane,
        "obligation": obligation.as_dict(),
    }
