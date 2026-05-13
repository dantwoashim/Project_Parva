# Protocol Governance

Parva Protocol governance is a draft process for changing public temporal contracts without weakening source policy or claim boundaries.

It does not create official calendar authority.

## Governance Scope

Governance covers:

- source review and tier assignment
- release manifest approval
- confidence label changes
- conflict handling
- schema versioning
- alpha conformance claims
- preview offline bundle contents
- security reporting
- deprecation and compatibility windows
- private data handling

## Release Decision Rules

Every public release should answer these questions before publication:

1. Which source tiers support the release?
2. Which claims are source-backed, calculated, preview-only, disputed, or unsupported?
3. Does the release expose any private future-BS value, source archive, client name, or private calibration artifact?
4. Do all schemas validate with examples?
5. Do public OpenAPI and static docs match the intended route profile?
6. Are unsupported operational claims routed to human review?

## Compatibility Claims

Compatibility levels are alpha conformance labels, not certification labels. A level can pass local checks and still require organization-specific review before production use.

`parva_full` means the local reference implementation passed the public protocol draft checks for core routes, schemas, manifests, trust logs, offline bundle integrity, SDK files, and negative cases. It does not mean official approval.

## Source Policy Changes

Source tier changes require a reason, an evidence pointer, a reviewer, and a release note. Weak third-party or software-table rows can support shadow comparison and review targeting, but they cannot support official-grade claims.

## Security Reporting

Reports involving route exposure, source leaks, secrets, private future values, or misleading accuracy claims should be treated as high priority. Public docs should be corrected quickly and private artifacts should be removed from tracking.
