# Temporal Trust Infrastructure Alpha

Project Parva is adding a public trust layer around calendar releases, source policy, and reconciliation events.

This is an alpha. It is meant to make temporal infrastructure easier to verify, not to claim official calendar authority.

## What This Alpha Adds

- release manifests with artifact hashes
- alpha release signature artifacts
- an append-only transparency-log prototype
- temporal SBOM schemas for downstream systems
- reconciliation event schemas for review workflows
- public claim boundaries for computed outputs

## Signing Model

The current signature artifact uses hash-only alpha verification:

```text
alpha_hash_only_sha256
```

This is not production-grade cryptographic signing. It is an interface and verification contract that can later be replaced by a real signing backend without changing the release workflow shape.

The verifier recomputes the release manifest hash and checks that the signature artifact still matches the manifest.

## Transparency Log

The alpha transparency log is an append-only JSONL file:

```text
data/public/transparency-log/parva-log.jsonl
```

Each row records a release event, release identifier, artifact hash, source-registry hash, timestamp, and signature reference.

## Temporal SBOM

A temporal SBOM lets a downstream system record which calendar release it depends on. This makes audit, rollback, and reconciliation easier when a calendar source or release changes.

## Reconciliation Events

Reconciliation events describe review workflows such as:

- official release verified
- release diff available
- risk label changed
- schedule review required
- future assumption resolved

These events should notify systems and reviewers. They should not silently update production databases without approval.

## Claim Boundary

Project Parva is not an official government calendar publication. Official publication overrides computed output.

Future-BS research output remains:

```text
computed_prediction_not_official
```

This alpha is not legal, tax, regulatory, or banking-contract final authority.
