---
status: draft
tier: 2
lane: protocol
last_verified: 2026-05-14
owner: protocol-team
---

# Protocol Lifecycle

Parva Protocol is a protocol draft. Its lifecycle is designed to keep public contracts stable while the implementation matures.

## Stages

| Stage | Meaning |
| --- | --- |
| Draft | Schema and behavior are being shaped |
| Alpha conformance | Local reference checks exist and run in CI |
| Preview offline bundle | Public artifacts can be verified without a live API |
| Release candidate | Contracts are stable enough for external review |
| Governed release | Signed artifacts, release approval, and compatibility policy are in place |

## Change Rules

Protocol changes should:

1. Update schemas and examples.
2. Update docs and compatibility descriptions.
3. Update conformance tests.
4. Run schema validation.
5. Run the public safety gate.
6. Avoid exposing private future-BS values or client-specific material.

## Deprecation

Breaking changes should include a migration note, a replacement surface, and a compatibility period where practical.

## Public Claim Boundary

Lifecycle status does not change the public claim boundary. Protocol artifacts remain decision-support and reproducibility tools unless an external authority or signed private deployment policy says otherwise.
