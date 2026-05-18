from __future__ import annotations

import json
from pathlib import Path

PROOF_PATHS = [
    "/v3/api/calendar/bs-to-gregorian",
    "/v3/api/calendar/convert",
    "/v3/api/calendar/validate-bs-date",
    "/v3/api/compliance/holiday",
    "/v3/api/compliance/evaluate-date",
    "/v3/api/enterprise/fiscal-year/{bs_year}",
    "/v3/api/enterprise/bs-months/{bs_year}",
    "/v3/api/calendar/panchanga",
]


def _openapi() -> dict:
    return json.loads(Path("docs/api-docs/openapi.public-reference.json").read_text(encoding="utf-8"))


def test_proof_schemas_are_defined_and_referenced_by_routes() -> None:
    schema = _openapi()
    components = schema["components"]["schemas"]
    for name in (
        "ProofReceipt",
        "ProofPack",
        "Timepack",
        "MembraneArtifact",
        "ReplayStatus",
        "NegativeMembrane",
        "UnsatMembrane",
        "BranchMembrane",
        "PanchangaProofArtifact",
        "BoundaryVector",
        "FieldProvenance",
        "SourceDocketRef",
        "MethodDocket",
        "EphemerisProviderMetadata",
        "PolicyDecisionTrace",
        "PayrollDateRiskReport",
    ):
        assert name in components

    for path in PROOF_PATHS:
        assert path in schema["paths"]
        for operation in schema["paths"][path].values():
            proof_params = [
                param
                for param in operation.get("parameters", [])
                if param.get("name") == "proof" and param.get("in") == "query"
            ]
            assert proof_params, path
            assert proof_params[0]["schema"]["enum"] == ["none", "compact", "audit", "replay", "membrane"]
            refs = json.dumps(operation)
            assert "#/components/schemas/ProofReceipt" in refs
            assert "#/components/schemas/BoundaryVector" in refs
            if "panchanga" in path:
                assert "#/components/schemas/EphemerisProviderMetadata" in refs
                assert "#/components/schemas/MethodDocket" in refs
