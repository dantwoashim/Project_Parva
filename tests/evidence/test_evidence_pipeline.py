from __future__ import annotations

import pytest
from app.evidence.checksums import sha256_json
from app.evidence.ingestion import ingest_source_record
from app.evidence.models import EvidencePacket
from app.evidence.normalization import normalize_source_rows
from app.evidence.review import mark_reviewed, promote_to_benchmark_candidate


def source_payload(**overrides):
    payload = {
        "source_id": "public_notice_001",
        "source_type": "notice",
        "source_reference": "https://example.org/notice",
        "source_tier": "public_witness",
        "public_safe": True,
        "authority_boundary": "source_backed_not_authority",
    }
    payload.update(overrides)
    return payload


def test_source_record_validates() -> None:
    record = ingest_source_record(source_payload())
    assert record.source_id == "public_notice_001"
    assert record.validate() == []


def test_checksum_is_deterministic() -> None:
    assert sha256_json({"b": 2, "a": 1}) == sha256_json({"a": 1, "b": 2})


@pytest.mark.parametrize("reference", ["file:///tmp/source.pdf", "D:" + "\\private\\source.pdf", "../private.pdf"])
def test_private_local_paths_are_rejected(reference: str) -> None:
    with pytest.raises(ValueError, match="local/private path"):
        ingest_source_record(source_payload(source_reference=reference))


def test_unsupported_authority_claims_are_rejected() -> None:
    with pytest.raises(ValueError, match="overclaims authority"):
        ingest_source_record(source_payload(authority_boundary="official_future_date"))


def test_reviewed_evidence_promotes_to_benchmark_candidate() -> None:
    source = ingest_source_record(source_payload())
    rows = [{"bs_date": "2082-01-01", "ad_date": "2025-04-14"}]
    packet = EvidencePacket(source, rows, normalize_source_rows(rows))
    reviewed = mark_reviewed(packet)
    candidate = promote_to_benchmark_candidate(reviewed)
    assert candidate["public_safe"] is True
    assert candidate["expected"]["source_metadata_required"] is True


def test_unreviewed_evidence_cannot_be_promoted() -> None:
    source = ingest_source_record(source_payload())
    rows = [{"bs_date": "2082-01-01", "ad_date": "2025-04-14"}]
    packet = EvidencePacket(source, rows, normalize_source_rows(rows))
    with pytest.raises(ValueError, match="unreviewed evidence"):
        promote_to_benchmark_candidate(packet)
