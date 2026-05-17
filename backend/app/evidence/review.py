"""Review and benchmark-promotion helpers for evidence packets."""

from __future__ import annotations

from typing import Any

from .models import EvidencePacket


def mark_reviewed(packet: EvidencePacket) -> EvidencePacket:
    return EvidencePacket(
        source=packet.source,
        extracted_rows=packet.extracted_rows,
        normalized_rows=packet.normalized_rows,
        review_status="reviewed",
        reviewer_required=False,
        benchmark_candidate=packet.benchmark_candidate,
    )


def promote_to_benchmark_candidate(packet: EvidencePacket) -> dict[str, Any]:
    if packet.review_status != "reviewed" or packet.reviewer_required:
        raise ValueError("unreviewed evidence cannot be promoted as source-backed")
    if not packet.source.public_safe:
        raise ValueError("private evidence cannot be promoted")
    first_row = packet.normalized_rows[0]
    return {
        "id": f"evidence_{packet.source.source_id}",
        "category": str(first_row.get("category") or "source_confidence_evidence_metadata"),
        "input": {"source_id": packet.source.source_id},
        "expected": {
            "source_metadata_required": True,
            "review_required": False,
            "machine_readable": True,
        },
        "public_safe": True,
        "authority_boundary": "technical_benchmark_not_authority",
        "scoring_dimensions": [
            "correctness",
            "source_awareness",
            "uncertainty_handling",
            "review_gate_behavior",
            "machine_readable_structure",
        ],
    }

