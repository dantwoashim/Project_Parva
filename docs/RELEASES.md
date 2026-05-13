# Calendar Releases

A Project Parva calendar release is a versioned bundle of public-safe metadata.

The current public release is:

```text
parva-bs-public-demo
```

It includes:

- release id
- release type
- status
- coverage metadata
- source policy
- artifact hashes
- schemas used
- capabilities
- default confidence
- warnings
- claim boundary

## Release Pinning

Trust endpoints accept release pinning through:

- query parameter: `release_id=parva-bs-public-demo`
- header: `x-parva-release-id: parva-bs-public-demo`

If a release id is unknown, the API returns a clear 404 error. The public release layer does not pretend old or private releases exist.

## Release Diff

Release diff is metadata-level in Layer 5. It compares:

- sources
- artifact hashes
- capabilities

It does not claim semantic holiday, payroll, banking, or business-day impact unless a later release explicitly computes that impact.

Example:

```bash
python scripts/parva_release_diff.py --from parva-bs-public-demo --to parva-bs-public-demo
```

## Claim Boundary

Release manifests are audit metadata, not legal certificates. Official publications and institutional policies override Project Parva computed or public-corpus output.
