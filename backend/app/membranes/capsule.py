"""Build a first complete conversion membrane."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.boundary.vector import BoundaryVector
from app.calendar.bikram_sambat import bs_to_gregorian
from app.canonicalization.normalize import canonical_json, canonicalize_query
from app.membranes.identity import membrane_identity_hash
from app.sources.hashing import canonical_json_hash
from app.trust.field_provenance import FieldProvenance, ProvenanceMap
from app.trust.taint import AuthorityTaint
from app.witnesses.schema import Witness

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_SNAPSHOT_PATH = PROJECT_ROOT / "data" / "sources" / "source_snapshot.json"


def _source_snapshot_hash() -> str:
    if not SOURCE_SNAPSHOT_PATH.exists():
        return "sha256:source_snapshot_unavailable"
    payload = json.loads(SOURCE_SNAPSHOT_PATH.read_text(encoding="utf-8"))
    return str(payload.get("snapshot_hash") or "sha256:source_snapshot_missing_hash")


def build_convert_bs_to_ad_capsule(year: int, month: int, day: int) -> dict[str, Any]:
    query = {
        "operation": "convert_bs_to_ad",
        "input": {"year": year, "month": month, "day": day},
        "context": {"calendar": "BS", "policy_id": "canonical@0.1.0"},
    }
    canonical_query = canonicalize_query(query)
    result = {"ad_date": bs_to_gregorian(year, month, day).isoformat()}
    provenance = ProvenanceMap(
        {
            "ad_date": FieldProvenance(
                "ad_date",
                AuthorityTaint.STRUCTURED_OFFICIAL,
                "lookup",
                source_docket_id="parva:src:v1:sample-2082-calendar-notice",
                witness_ids=("parva:review:v1:sample",),
            )
        }
    )
    boundary = BoundaryVector.from_provenance(provenance)
    source_snapshot_hash = _source_snapshot_hash()
    witness = Witness(
        operation="convert_bs_to_ad",
        input_hash=f"sha256:{canonical_json_hash(canonical_query)}",
        output_hash=f"sha256:{canonical_json_hash(result)}",
        verifier="parva.convert_bs_to_ad",
        verifier_version="1.0.0",
        method_parameters={"calendar": "BS", "source_snapshot_hash": source_snapshot_hash},
        source_refs=("parva:src:v1:sample-2082-calendar-notice",),
    )
    capsule = {
        "kind": "parva_membrane",
        "membrane_kind": "positive",
        "canonical_query": canonical_query,
        "canonical_query_json": canonical_json(canonical_query),
        "identity_hash": membrane_identity_hash(canonical_query),
        "result": result,
        "boundary": boundary.as_dict(),
        "field_provenance": provenance.as_dict(),
        "source_docket_ids": ["parva:src:v1:sample-2082-calendar-notice"],
        "source_snapshot_hash": source_snapshot_hash,
        "proof_pack": {
            "level": "audit",
            "verifier": "parva.convert_bs_to_ad",
            "verifier_version": "1.0.0",
            "method_parameters": {"calendar": "BS", "source_snapshot_hash": source_snapshot_hash},
            "source_artifacts": {
                "source_docket_ids": ["parva:src:v1:sample-2082-calendar-notice"],
                "source_snapshot_hash": source_snapshot_hash,
            },
            "steps": [
                {
                    "operation": "canonicalize_query",
                    "output_hash": f"sha256:{canonical_json_hash(canonical_query)}",
                },
                {
                    "operation": "convert_bs_to_ad",
                    "output_hash": f"sha256:{canonical_json_hash(result)}",
                },
            ],
        },
        "witness": witness.as_dict(),
    }
    capsule["witness_hash"] = witness.witness_id
    return capsule
