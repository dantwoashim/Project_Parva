---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# MoHA Holiday Release Workflow

Status: Phase 06 precise scaffold. Full holiday row extraction remains a future implementation task after source samples are supplied.

Parva can ingest MoHA holiday release metadata without claiming MoHA authority. MoHA remains the authority for its own notices.

## Workflow

1. Acquire the source notice from MoHA or an official publication path.
2. Record source metadata: URL or retained filename, BS year, source authority, source tier, retrieval time, and checksum where a file is retained.
3. Compute a file hash for retained local files.
4. Retain or link the human-readable notice according to redistribution rights.
5. Extract holiday rows into a machine-readable draft release.
6. Validate the release schema.
7. Generate evidence packets for changed holiday claims.
8. Update the public release manifest and hashes.
9. Run trust verification.
10. Exercise the API route that serves the release with source/confidence metadata.
11. Generate and verify the offline bundle.

## Scaffold Command

The current scaffold records source metadata and required next steps:

```bash
python scripts/sources/ingest_moha_holiday_release.py --source path-or-url --year 2083 --output data/public/releases/
```

For a local file, the scaffold computes `source_sha256`. For a URL, it records the URL and marks the hash as deferred until a source file is retained.

## Output Status

The scaffold writes `workflow_status = scaffold_requires_human_structuring`.

It does not yet parse arbitrary PDFs or issue machine-readable holiday rows. That is intentional until source samples, redistribution rules, and review ownership are available.

## Acceptance Gate For A Real Release

A real MoHA-backed public release is accepted only when:

- source metadata exists
- retained-file hash or public source URL exists
- extracted rows have source ids and confidence
- schema validation passes
- evidence packets exist for changed holiday claims
- release manifest hashes are regenerated
- `python scripts/parva_trust_verify.py` passes
- offline bundle verification passes
- API output says Parva is not legal or official authority

