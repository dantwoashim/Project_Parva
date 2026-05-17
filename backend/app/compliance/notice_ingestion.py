"""Semi-manual notice-to-obligation ingestion."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.compliance.obligation import Obligation
from app.compliance.requirement import document_requirement
from app.membranes.capsule import build_convert_bs_to_ad_capsule
from app.sources.hashing import canonical_json_hash

BS_DATE_RE = re.compile(r"(?P<year>20\d{2})-(?P<month>\d{2})-(?P<day>\d{2})")
FIELD_RE = re.compile(r"^(?P<key>issuer|published|effective|deadline|action|affected_party|jurisdiction):\s*(?P<value>.+)$", re.I)


@dataclass(frozen=True)
class NoticeExtraction:
    issuer: str
    publication_date: str | None
    effective_date: str | None
    deadline: str
    required_action: str
    affected_party: str
    jurisdiction: str
    source_excerpt: str
    review_status: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "issuer": self.issuer,
            "publication_date": self.publication_date,
            "effective_date": self.effective_date,
            "deadline": self.deadline,
            "required_action": self.required_action,
            "affected_party": self.affected_party,
            "jurisdiction": self.jurisdiction,
            "source_excerpt": self.source_excerpt,
            "review_status": self.review_status,
        }


def _field_map(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = FIELD_RE.match(line.strip())
        if match:
            fields[match.group("key").lower()] = match.group("value").strip()
    return fields


def _extract_notice(text: str) -> NoticeExtraction:
    fields = _field_map(text)
    date_matches = [match.group(0) for match in BS_DATE_RE.finditer(text)]
    deadline = fields.get("deadline") or (date_matches[-1] if date_matches else None)
    if not deadline:
        raise ValueError("notice requires an explicit BS deadline")
    review_status = "review_required" if any(token in text.lower() for token in ("approx", "unclear", "tentative")) else "review_required"
    return NoticeExtraction(
        issuer=fields.get("issuer", "unreviewed_notice_issuer"),
        publication_date=fields.get("published"),
        effective_date=fields.get("effective") or (date_matches[0] if len(date_matches) > 1 else None),
        deadline=deadline,
        required_action=fields.get("action", "Review date-sensitive workflow before deadline."),
        affected_party=fields.get("affected_party", "unspecified_party"),
        jurisdiction=fields.get("jurisdiction", "np:review_required"),
        source_excerpt=text.strip()[:500],
        review_status=review_status,
    )


def ingest_notice(text: str, *, source_docket_id: str = "parva:src:v1:review-required-notice") -> dict:
    extraction = _extract_notice(text)
    year, month, day = (int(part) for part in extraction.deadline.split("-"))
    docket = {
        "source_docket_id": source_docket_id,
        "source_text_hash": f"sha256:{canonical_json_hash({'text': text})}",
        "source_text_hash_boundary": "notice_source_text_not_legal_authority",
        "review_required": True,
    }
    receipt = {
        "receipt_id": f"parva:extract:v1:{canonical_json_hash(extraction.as_dict())[:16]}",
        "extracted_deadline": extraction.deadline,
        "extraction": extraction.as_dict(),
        "review_status": extraction.review_status,
        "reviewer_required": True,
    }
    deadline_membrane = build_convert_bs_to_ad_capsule(year, month, day)
    obligation = Obligation(
        obligation_id=f"parva:obl:v1:{canonical_json_hash({'deadline': extraction.deadline, 'source': source_docket_id})[:16]}",
        claim_type="deadline_claim",
        source_docket_id=docket["source_docket_id"],
        applicability={
            "entity_type": extraction.affected_party,
            "jurisdiction": extraction.jurisdiction,
            "industry": "review_required",
            "institution": extraction.issuer,
            "role": "operator",
        },
        effective_bs=extraction.effective_date or extraction.deadline,
        deadline_bs=extraction.deadline,
        required_action=extraction.required_action,
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
