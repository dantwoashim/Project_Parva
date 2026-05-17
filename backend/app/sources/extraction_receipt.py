"""Extraction receipt schema tying normalized fields to source regions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.sources.hashing import canonical_json_hash


@dataclass(frozen=True)
class ExtractionReceipt:
    source_docket_id: str
    source_region: dict[str, Any]
    extracted_text: str
    normalization_rule: str
    normalized_row: dict[str, Any]
    review_status: str = "reviewed"
    manual_patch_applied: bool = False
    manual_patch_reason: str | None = None

    @property
    def normalized_row_hash(self) -> str:
        return canonical_json_hash(self.normalized_row)

    @property
    def receipt_id(self) -> str:
        return f"parva:extract:v1:sha256:{canonical_json_hash(self.as_dict(include_id=False))}"

    def as_dict(self, *, include_id: bool = True) -> dict[str, Any]:
        payload = {
            "kind": "extraction_receipt",
            "source_docket_id": self.source_docket_id,
            "source_region": self.source_region,
            "ocr_text": self.extracted_text,
            "normalization_rule": self.normalization_rule,
            "manual_patch": {
                "applied": self.manual_patch_applied,
                "reason": self.manual_patch_reason,
            },
            "normalized_row_hash": self.normalized_row_hash,
            "normalized_row": self.normalized_row,
            "review_status": self.review_status,
        }
        if include_id:
            payload["receipt_id"] = self.receipt_id
        return payload
