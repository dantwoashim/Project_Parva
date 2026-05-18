# Route Proof Contract Matrix

This matrix records stable public routes with proof-mode contract tests. It does not claim official authority or external validation.

| Route | Method | Operation | Proof modes | Test | OpenAPI refs | Status |
| --- | --- | --- | --- | --- | --- | --- |
| /v3/api/calendar/bs-to-gregorian | POST | bs_to_ad | none, compact, audit, replay, membrane | tests/contract/test_route_proof_contract_matrix.py | ProofReceipt, MembraneArtifact, BoundaryVector, FieldProvenance | covered |
| /v3/api/calendar/convert | GET | ad_to_bs | none, compact, audit, replay, membrane | tests/contract/test_route_proof_contract_matrix.py | ProofReceipt, MembraneArtifact, BoundaryVector, FieldProvenance | covered |
| /v3/api/calendar/validate-bs-date | GET | validate_bs_date | none, compact, audit, replay, membrane | tests/contract/test_route_proof_contract_matrix.py | ProofReceipt, NegativeMembrane, BoundaryVector, FieldProvenance | covered |
| /v3/api/compliance/holiday | GET | holiday | none, compact, audit, replay, membrane | tests/contract/test_route_proof_contract_matrix.py | ProofReceipt, MembraneArtifact, BoundaryVector, FieldProvenance | covered |
| /v3/api/compliance/evaluate-date | POST | working_day | none, compact, audit, replay, membrane | tests/contract/test_route_proof_contract_matrix.py | ProofReceipt, MembraneArtifact, BoundaryVector, FieldProvenance | covered |
| /v3/api/enterprise/fiscal-year/{bs_year} | GET | fiscal_year | none, compact, audit, replay, membrane | tests/contract/test_route_proof_contract_matrix.py | ProofReceipt, MembraneArtifact, BoundaryVector, FieldProvenance | covered |
| /v3/api/enterprise/bs-months/{bs_year} | GET | bs_months | none, compact, audit, replay, membrane | tests/contract/test_route_proof_contract_matrix.py | ProofReceipt, BranchMembrane, BoundaryVector, FieldProvenance | covered |
| /v3/api/calendar/panchanga | GET | panchanga_summary | none, compact, audit, replay, membrane | tests/contract/test_route_proof_contract_matrix.py | ProofReceipt, PanchangaProofArtifact, MethodDocket, EphemerisProviderMetadata, BoundaryVector, FieldProvenance | covered |
