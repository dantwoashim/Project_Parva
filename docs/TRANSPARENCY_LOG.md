# Transparency Log

Project Parva includes an alpha append-only transparency-log prototype for public release events.

The current log is:

```text
data/public/transparency-log/parva-log.jsonl
```

## What Gets Logged

Each log row records:

- event name
- release identifier
- release artifact hash
- source-registry hash
- timestamp
- signature artifact reference

The first supported public event is:

```text
calendar.release.published
```

The reconciliation event schema also defines review-oriented events for release diffs, risk-label changes, schedule review, and resolved assumptions.

## Verification

Run:

```bash
python tools/trust/verify_log.py
```

The verifier checks:

- valid JSONL rows
- supported event names
- SHA-256 reference shape
- signature reference existence
- duplicate release artifact entries
- public-safety text patterns

## Limitations

This is an alpha JSONL prototype. It is not yet a Merkle-tree transparency system, external public ledger, or production signing service.

Future versions may add Merkle proofs, external transparency anchors, stronger key management, and organization-specific approval workflows.

## Claim Boundary

The log proves that a public release event was recorded in this repository. It does not turn computed output into official publication.
