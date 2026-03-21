# Release Candidate Technical Dossier

## Candidate Identity

- Candidate date:
- Candidate SHA:
- Candidate tag:
- Prepared from clean checkout: yes/no

## Runtime Matrix

- Python:
- Node:
- Operating system:
- Browser smoke environment:

## Provenance

- Manifest version:
- Canonical engine id:
- Dataset hash:
- Rules hash:
- Dependency lock hash:
- Attestation mode:
- Attestation key id:

## Release Gates

- `scripts/verify_environment.py`
- `scripts/release/check_repo_hygiene.py`
- `scripts/release/check_render_blueprint.py`
- `scripts/release/check_sdk_install.py`
- `scripts/release/check_contract_freeze.py`
- `scripts/release/check_provenance_readiness.py`
- backend tests
- frontend clean install
- frontend lint/tests/build
- frontend bundle budget
- security audit
- browser smoke
- golden journeys
- launch signoff
- source archive

## User-Facing Risk Review

- degraded-state behavior reviewed:
- no hidden fallback date behavior confirmed:
- accessibility/dialog regression check:
- launch-critical journeys reviewed:
- timezone rendering spot-check:
- known limits accepted for this candidate:

## Artifact Inventory

- Source archive:
- Public-beta dossier:
- Conformance report:
- Authority dashboard:
- Browser smoke output:
- Golden journeys output:
- Bundle budget report:
- Security audit report:
- Launch signoff document:

## Decision

- Release candidate approved: yes/no
- Approver:
- Notes:
