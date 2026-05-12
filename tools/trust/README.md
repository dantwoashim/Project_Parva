# Temporal Trust Tools

These tools implement the first public alpha of Parva Temporal Trust Infrastructure.

The current signing flow is hash-only alpha verification. It does not claim production-grade cryptographic signing. It provides a stable interface for release identity, artifact hashes, transparency-log entries, and later replacement with a real signing backend.

## Create an Alpha Signature

```bash
python tools/trust/sign_release.py --signed-at 2026-05-12T00:00:00Z
```

Output:

```text
data/public/releases/parva-bs-public-demo.signature.json
```

## Verify an Alpha Signature

```bash
python tools/trust/verify_release_signature.py
```

The verifier recomputes the release manifest hash and checks that the alpha signature artifact still matches it.

## Append a Transparency Log Entry

```bash
python tools/trust/append_log_entry.py --timestamp 2026-05-12T00:00:00Z
```

Output:

```text
data/public/transparency-log/parva-log.jsonl
```

## Verify the Transparency Log

```bash
python tools/trust/verify_log.py
```

The verifier checks JSONL shape, event names, SHA-256 references, signature references, duplicate release entries, and public-safety text patterns.

## Safety Boundary

These tools work on public demo artifacts. They do not expose private future-BS vectors, corrected future values, private model internals, or client-specific workflows.
