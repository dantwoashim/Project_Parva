"""Models and validation for public evidence packets."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from .checksums import sha256_json

ALLOWED_SOURCE_TYPES = {"pdf", "csv", "notice", "web_page", "manual_public_reference"}
ALLOWED_SOURCE_TIERS = {
    "official_verified",
    "printed_verified",
    "public_witness",
    "publisher_reference",
    "software_table_reference",
    "third_party_reference",
    "needs_review",
}
ALLOWED_REVIEW_STATUS = {"unreviewed", "reviewed", "rejected"}
FORBIDDEN_AUTHORITY_CLAIMS = {
    "government_authority",
    "legal_authority",
    "tax_authority",
    "banking_authority",
    "payroll_authority",
    "official_future_date",
    "religious_authority",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _is_local_or_private_reference(reference: str) -> bool:
    parsed = urlparse(reference)
    if parsed.scheme in {"file"}:
        return True
    if parsed.scheme in {"http", "https"}:
        host = (parsed.hostname or "").lower()
        return host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".local")
    return "\\" in reference or reference.startswith(("/", "./", "../")) or ":" in reference[:4]


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    source_type: str
    source_reference: str
    source_tier: str
    public_safe: bool = True
    authority_boundary: str = "source_backed_not_authority"
    ingestion_time: str = field(default_factory=utc_now_iso)

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.source_id:
            issues.append("source_id is required")
        if self.source_type not in ALLOWED_SOURCE_TYPES:
            issues.append(f"unsupported source_type: {self.source_type}")
        if self.source_tier not in ALLOWED_SOURCE_TIERS:
            issues.append(f"unsupported source_tier: {self.source_tier}")
        if not self.public_safe:
            issues.append("source record must be public_safe")
        if _is_local_or_private_reference(self.source_reference):
            issues.append("source_reference must not be a local/private path")
        if self.authority_boundary in FORBIDDEN_AUTHORITY_CLAIMS:
            issues.append("authority_boundary overclaims authority")
        return issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "source_reference": self.source_reference,
            "source_tier": self.source_tier,
            "ingestion_time": self.ingestion_time,
            "public_safe": self.public_safe,
            "authority_boundary": self.authority_boundary,
        }


@dataclass(frozen=True)
class EvidencePacket:
    source: SourceRecord
    extracted_rows: list[dict[str, Any]]
    normalized_rows: list[dict[str, Any]]
    review_status: str = "unreviewed"
    reviewer_required: bool = True
    benchmark_candidate: bool = False

    def validate(self) -> list[str]:
        issues = self.source.validate()
        if self.review_status not in ALLOWED_REVIEW_STATUS:
            issues.append(f"unsupported review_status: {self.review_status}")
        if not self.extracted_rows:
            issues.append("extracted_rows must not be empty")
        if not self.normalized_rows:
            issues.append("normalized_rows must not be empty")
        if self.benchmark_candidate and self.review_status != "reviewed":
            issues.append("benchmark candidates require reviewed evidence")
        if self.benchmark_candidate and self.reviewer_required:
            issues.append("benchmark candidates cannot still require reviewer action")
        if self.source.authority_boundary in FORBIDDEN_AUTHORITY_CLAIMS:
            issues.append("evidence packet overclaims authority")
        return issues

    def to_dict(self) -> dict[str, Any]:
        body = {
            **self.source.to_dict(),
            "extracted_rows": self.extracted_rows,
            "normalized_rows": self.normalized_rows,
            "review_status": self.review_status,
            "reviewer_required": self.reviewer_required,
            "benchmark_candidate": self.benchmark_candidate,
        }
        body["checksum"] = sha256_json({key: value for key, value in body.items() if key != "checksum"})
        return body

