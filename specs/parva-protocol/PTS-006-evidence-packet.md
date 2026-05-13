# PTS-006 Evidence Packet

## Purpose

Evidence packets bind a deterministic result to its input, release, source context, confidence, claim boundary, fact IDs, and integrity hash.

## Required fields

- `packet_id`
- `packet_type`
- `input`
- `result`
- `release`
- `confidence`
- `claim_boundary`
- `integrity`

## Semantics

An evidence packet remains historically valid for the release that generated it. It may become stale for current use if supporting facts, sources, rules, or profiles change.
