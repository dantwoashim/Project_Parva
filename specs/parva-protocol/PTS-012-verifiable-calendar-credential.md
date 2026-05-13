# PTS-012 Verifiable Calendar Credential

## Purpose

A Parva Calendar Credential is a portable hash-only preview credential for a temporal claim.

## Required fields

- `credential_id`
- `protocol_version`
- `issuer`
- `claim`
- `release_id`
- `source_ids`
- `confidence`
- `claim_boundary`
- `status`
- `proof`

## Boundary

The public preview credential uses `hash_only_preview`. It does not claim production-grade signature authority.
