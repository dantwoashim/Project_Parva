# PTS-004 Release Manifest

## Purpose

A release manifest pins public temporal artifacts, source registries, schemas, and checksums.

## Required fields

- `release_id`
- `release_type`
- `generated_at`
- `artifact_hashes`
- `claim_boundary`

## Validation

Artifact paths must stay within the repository or bundle root, and hashes must match file content.
