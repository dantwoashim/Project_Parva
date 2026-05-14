# Trust And Data Governance

Status: Phase 06 governed public trust layer.

Project Parva publishes source-aware calendar, fiscal, festival, panchanga, protocol, and evidence metadata. This governance layer keeps that metadata reproducible without turning Parva into official authority.

Parva is not a government calendar publication, legal authority, tax authority, payroll authority, regulatory authority, or banking-contract authority. Official publications and institution-approved policies override Parva output.

## Governed Public Artifacts

| Artifact class | Canonical location | Public? | Verification |
|---|---|---:|---|
| Public release manifests | `data/public/releases/*.manifest.json` | Yes | `python scripts/parva_trust_verify.py` |
| Public source registries | `data/public/releases/*.sources.json` | Yes | `python scripts/parva_trust_verify.py` |
| Public trust log | `data/public/trust/parva-trust-log.jsonl` | Yes | `python scripts/parva_trust_verify.py` |
| Public transparency log | `data/public/transparency-log/parva-log.jsonl` | Yes | `python tools/trust/verify_log.py` |
| Runtime validation artifacts | `data/validation/public/`, `backend/data/public_artifacts/` | Yes | `python -m pytest tests/architecture -q` |
| Protocol schemas | `schemas/parva-protocol/` | Yes | `python tools/validate_schemas.py` |
| Offline bundle | `dist/parva-offline-bundle/` when generated | Yes | `python scripts/parva_offline_verify.py dist/parva-offline-bundle` |
| Private source archives | `data/source_archive/` local only | No | Opt-in private tests only |
| Private future-BS artifacts | `data/future_bs/private/` local only | No | Phase 07 research governance |

## Release Identity

The active public release id is `parva-bs-public-demo`. Public routes default to that release unless a route explicitly accepts a supported `release_id`.

Release identity is separate from application version, SDK version, and protocol version. A software release does not make a calendar row official.

## Evidence Rules

Every public temporal claim should carry as much of this envelope as the route can support:

- `source_tier`
- `confidence`
- `release_id`
- `trace_id`
- `warnings`
- `claim_boundary`
- `maturity`
- evidence packet id or evidence path where applicable

Evidence packets currently exist for date conversion, compliance decisions, and public RuleLang execution. Impact reports, credential issue/verify flows, and official holiday ingestion have public scaffolds or bounded report surfaces and are tracked in generated artifact `reports/phase_06_trust_data_governance/evidence_packet_coverage.md`.

## Public And Private Boundary

Public trust artifacts must not include:

- private source archive paths
- private future-BS paths or exact private outputs
- local absolute filesystem paths
- private credentials
- client-specific audit material
- test-only fixture paths as public quality evidence

Allowed public mentions of private paths are documentation-only boundary descriptions, not artifact references. Public verification is enforced by:

```bash
python scripts/check_path_leaks.py
python -m pytest tests/trust/test_public_artifacts_no_private_paths.py -q
python -m pytest tests/architecture/test_runtime_does_not_depend_on_tests_fixtures.py -q
```

## Deterministic Rebuild

Public release hashes are rebuilt by:

```bash
python scripts/release/regenerate_public_release_hashes.py --check
python scripts/release/regenerate_public_release_hashes.py --write
python scripts/parva_trust_verify.py
```

See `docs/TRUST_ARTIFACT_REGENERATION_RUNBOOK.md` for approval, drift review, rollback, and CI behavior.

## Source Authority

Canonical source tiers are documented in `docs/SOURCE_AUTHORITY_POLICY.md` and implemented in `backend/app/core/source_authority.py`.

No fixture, calculated, research-private, unknown, weak third-party, or software-table row may support official-looking claims. MoHA, NPNS, NRB, publishers, and other authorities remain the source authority for their own publications.
