# Transparency Log (Week 41-44)

Project Parva now maintains an append-only transparency log.

## Storage
- Log: `/Users/rohanbasnet14/Documents/Project Parva/data/transparency/log.jsonl`
- Anchor mirror log: `/Users/rohanbasnet14/Documents/Project Parva/data/transparency/anchors.jsonl`

## Entry Fields
- `entry_id`
- `timestamp` (UTC)
- `event_type`
- `payload`
- `prev_hash`
- `entry_hash`
- `signature` (`sha256:<entry_hash>`)

## Integrity
The log is hash-chained:
- each entry stores `prev_hash`
- `entry_hash` is computed from canonicalized entry body
- `verify_log_integrity()` checks hash, chain, and signature consistency

## API
- `GET /v2/api/provenance/transparency/log`
- `GET /v2/api/provenance/transparency/audit`
- `GET /v2/api/provenance/transparency/replay`
- `POST /v2/api/provenance/transparency/append`
- `GET /v2/api/provenance/transparency/anchor/prepare`
- `POST /v2/api/provenance/transparency/anchor/record`
- `GET /v2/api/provenance/transparency/anchors`

## CLI Tools
- `PYTHONPATH=backend python3 backend/tools/transparency_audit.py`
- `PYTHONPATH=backend python3 backend/tools/transparency_anchor_prepare.py --note "beta-cycle"`
