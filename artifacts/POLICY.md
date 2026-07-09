# Artifact Policy

Project Parva separates source files, tracked public artifacts, generated
reports, and private/local artifacts.

## Source Files

Source files are hand-authored code, docs, schemas, fixtures, and public source
archives required to understand or verify the public project.

## Tracked Public Artifacts

Tracked artifacts are allowed only when they are part of the public verification
surface or reviewer packet. Each tracked artifact should have one of:

- a regeneration command,
- a checksum or manifest entry,
- a documentation link explaining why it is tracked.

Examples:

- `reports/conformance/public-issue-suite-summary.json`
- `reports/conformance/public-issue-suite-summary.md`
- `docs/api-docs/openapi*.json`
- `data/source_archive/moha/manifest.json`

## Generated Local Artifacts

Generated local outputs belong in ignored paths such as `reports/`, `output/`,
`tmp/`, coverage folders, frontend build folders, package build folders, and
private future-BS research folders.

## Private Artifacts

Private source archives, private future-BS corpora, customer data, local
research runs, and exact future prediction vectors must not be required by the
public verification gate.

## Review Rule

Before adding a new tracked artifact, document why it is tracked and how a
reviewer can verify that it is current.
