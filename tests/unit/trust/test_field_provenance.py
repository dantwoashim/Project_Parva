from __future__ import annotations

import pytest
from app.boundary.vector import BoundaryVector
from app.trust.field_provenance import FieldProvenance, ProvenanceMap
from app.trust.serialization import serialize_trust_result
from app.trust.taint import AuthorityTaint, TaintFlag


def test_field_provenance_requires_every_result_field() -> None:
    provenance = ProvenanceMap(
        {
            "ad_date": FieldProvenance(
                field_path="ad_date",
                authority=AuthorityTaint.STRUCTURED_OFFICIAL,
                derivation="lookup",
            )
        }
    )
    with pytest.raises(ValueError):
        provenance.require_all_fields({"ad_date": "2025-04-14", "holiday": False})


def test_boundary_uses_weakest_field_authority() -> None:
    provenance = ProvenanceMap(
        {
            "ad_date": FieldProvenance("ad_date", AuthorityTaint.STRUCTURED_OFFICIAL, "lookup"),
            "month_length": FieldProvenance(
                "month_length",
                AuthorityTaint.STATIC_REFERENCE,
                "lookup",
                flags=frozenset({TaintFlag.REVIEW_REQUIRED}),
            ),
        }
    )
    boundary = BoundaryVector.from_provenance(provenance)
    assert boundary.authority == AuthorityTaint.STATIC_REFERENCE
    assert boundary.review_state == "required"


def test_source_backed_field_requires_source_docket() -> None:
    provenance = ProvenanceMap(
        {
            "ad_date": FieldProvenance(
                field_path="ad_date",
                authority=AuthorityTaint.STRUCTURED_OFFICIAL,
                derivation="normalized_source_row",
            )
        }
    )
    with pytest.raises(ValueError, match="source docket lineage"):
        provenance.require_source_backed_dockets()


def test_trust_serializer_requires_full_provenance_and_dockets() -> None:
    provenance = ProvenanceMap(
        {
            "ad_date": FieldProvenance(
                field_path="ad_date",
                authority=AuthorityTaint.ARCHIVED_OFFICIAL,
                derivation="normalized_source_row",
                source_docket_id="parva:src:v1:test",
                review_state="reviewed",
            )
        }
    )
    serialized = serialize_trust_result({"ad_date": "2025-04-14"}, provenance)
    assert serialized["weakest_authority"] == "archived_official"
    assert serialized["field_provenance"]["ad_date"]["source_docket_id"] == "parva:src:v1:test"
