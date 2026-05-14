# Trust Artifact Regeneration Runbook

Status: Phase 06 public release hash runbook.

Use this runbook when a public source registry, release manifest, release schema, protocol schema, or bundled public artifact changes.

## Canonical Commands

```bash
python scripts/release/regenerate_public_release_hashes.py --check
python scripts/release/regenerate_public_release_hashes.py --write
python scripts/parva_trust_verify.py
```

Use Python 3.11. On Windows, the working interpreter for this run was the user-local Python 3.11 executable under:

```text
%LOCALAPPDATA%\Programs\Python\Python311\python.exe
```

## When To Regenerate

Regenerate when any file listed in `data/public/releases/parva-bs-public-demo.manifest.json` changes, including:

- `data/public/releases/parva-bs-public-demo.sources.json`
- schemas listed in `schemas_used`
- protocol credential, conformance, or offline bundle schemas
- public trust artifacts that become manifest artifacts in a later release

Do not regenerate for private archives, private future-BS artifacts, local caches, generated reports, or test-only fixtures.

## Approval Rule

Hash changes require review by the release owner for the changed artifact class:

| Change | Approval |
|---|---|
| Source registry content | Source/release reviewer |
| Schema contract | Protocol/schema reviewer |
| Claim boundary text | Trust reviewer |
| Offline bundle contents | Release reviewer |
| Official-source ingestion | Human source reviewer plus release reviewer |

## Review Drift

1. Run `python scripts/release/regenerate_public_release_hashes.py --check`.
2. If it fails, inspect the changed artifact with `git diff`.
3. Confirm the artifact is public-safe and source-authority labels are correct.
4. Run `python scripts/release/regenerate_public_release_hashes.py --write`.
5. Re-run `python scripts/parva_trust_verify.py`.
6. Re-run `python scripts/check_path_leaks.py`.
7. Update the Phase 06 rebuild report with changed files and command output.

## Private Artifact Exclusion

The regeneration script only rewrites the public manifest and alpha hash-only signature. It must not add:

- `data/source_archive/`
- `data/future_bs/private/`
- local absolute paths
- credentials
- client-specific files
- raw third-party archives without redistribution review

## CI Behavior

Scheduled trust drift CI runs:

```bash
python scripts/parva_trust_verify.py
python tools/validate_schemas.py
python scripts/parva_protocol_verify.py
```

The public verification workflow also runs `python scripts/release/verify_public.py`.

## Rollback

Rollback means reverting the changed public artifact and regenerating the manifest/signature hashes from the restored artifact. Do not edit hash fields by hand.

If a release has already been published externally, create a superseding manifest rather than mutating the public release silently.
