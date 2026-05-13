# Trust Infrastructure

Project Parva exposes a public temporal trust layer for source registry records, release manifests, trust logs, release diffs, and evidence packets.

This layer makes answers auditable. It does not turn Parva into an official government calendar publication, legal authority, tax authority, payroll authority, or banking-contract authority.

## Core Concepts

| Concept | Meaning |
|---|---|
| Source registry | Public-safe metadata about the source families associated with a release |
| Release manifest | A versioned description of sources, artifacts, capabilities, claim boundaries, and warnings |
| Trust log | A hash-linked public log of trust events for the release layer |
| Release diff | A metadata-level comparison between two release manifests |
| Evidence packet | A hashable explanation of how a temporal answer was produced |
| Release pinning | A request can name a release id and fail clearly if that release is unknown |

## Active Public Release

The current public release id is:

```text
parva-bs-public-demo
```

Public APIs default to this release unless a supported request accepts a different `release_id`.

## Source Tiers

Layer 5 source tiers are:

- `official`
- `semi_official`
- `public_corpus`
- `publisher`
- `calculated`
- `fixture`
- `research`
- `private`
- `unknown`

Only a truly documented official source may use `official`. Fixtures, research outputs, and calculated surfaces must stay labeled as such.

## Public Boundary

Public trust endpoints expose metadata and evidence packets. They do not expose private archives, private future-BS vectors, corrected future values, private model internals, or client-specific workflows.

Future-BS research remains:

```text
computed_prediction_not_official
```

## Verification

Run:

```bash
python scripts/parva_trust_verify.py
```

The verifier checks the release manifest, source registry, artifact hashes, alpha signature, transparency log, and Layer 5 trust log.
