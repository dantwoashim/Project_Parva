# Release Manifests

Project Parva release manifests describe which public artifacts, schemas, source policy, and claim boundary belong to a calendar release.

The first public demo manifest is:

```text
data/public/releases/parva-bs-public-demo.manifest.json
```

It is a metadata release for public demo and conformance use. It is not an official government calendar publication.

## Why Releases Exist

Calendar infrastructure needs reproducible context. A conversion result is easier to review when it can point to:

- a release identifier
- a source policy
- schema versions
- artifact hashes
- a claim boundary

This lets SDKs, private deployments, and reviewers verify that a result was produced against the expected public contract.

## What The Manifest Contains

The public release manifest includes:

- `release_id`
- `calendar`
- `coverage`
- `source_policy`
- `publication_status`
- `artifact_hashes`
- `generated_at`
- `schemas_used`
- `claim_boundary`

The public demo manifest sets `future_values_included` to `false`.

## Artifact Hashes

Every listed artifact has a SHA-256 digest. The verifier recomputes the digest from the file in the repository and compares it with the manifest.

Run:

```bash
python tools/release/verify_release.py data/public/releases/parva-bs-public-demo.manifest.json
```

## Claim Boundary

Official publication overrides public demo metadata and computed output.

Future-BS research output remains:

```text
computed_prediction_not_official
```

The release manifest is not legal, tax, regulatory, or banking-contract final authority.

## Alpha Limitations

- The first manifest is unsigned.
- It verifies local repository artifacts only.
- It does not include private future-BS vectors or private model artifacts.
- It is intended as a public contract foundation for future signed releases.
