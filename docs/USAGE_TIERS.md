# Usage Tiers

This document describes the recommended packaging model for Project Parva.

It is a go-to-market guide, not a code-enforced billing system.

## Principles

- Keep the broad public utility free.
- Charge for hosting, evidence access, integration work, and operational support.
- Do not promise stronger accuracy or authority claims than the evidence artifacts support.

## Recommended free tier

What stays free:

- public `v3` read-only API routes
- static embeds under `frontend/public/embed/`
- public frontend experience
- public festival feeds
- source access required by the AGPL path

Good fit:

- community sites
- student projects
- informational portals
- early institutional evaluation

## Recommended partner tier

What is reasonable to charge for:

- managed hosting
- white-label deployment
- onboarding and integration support
- `commercial.read` access to non-public evidence routes
- provenance and conformance review workflows
- operational reviews and rollout support

Suggested partner surfaces:

- `/v3/api/reliability/*`
- `/v3/api/spec/*`
- `/v3/api/public/artifacts/*`
- `/v3/api/provenance/root`
- `/v3/api/provenance/proof`
- `/v3/api/provenance/verify/trace/*`

## Recommended institutional package

Best positioned for:

- municipalities
- tourism boards
- temples and trusts
- publishers
- schools and universities

Package contents:

- one managed deployment
- one or more embed widgets
- API onboarding
- launch checklist review
- known-limits and public-beta disclosure setup
- source publication compliance for the deployed build

## What should not be sold yet

Avoid selling these as if they already exist in a finished form:

- strict uptime SLAs enforced by code
- enterprise multi-tenant billing
- final scholarly authority over all regional rule variants
- production-grade push integration ecosystem
- hard guarantees beyond the current evidence artifacts

## Practical zero-budget monetization path

1. Keep public `v3` and embeds free.
2. Offer setup and hosting for institutions that do not want to self-deploy.
3. Offer evidence-backed access using `commercial.read`.
4. Charge for integration, customization, data presentation, training, and support.

## Message discipline

Safe language:

- public beta
- explainable
- traceable
- profile-based
- known limits

Unsafe language at the current stage:

- definitive authority
- zero issues
- guaranteed perfect accuracy
- final answer for every tradition and locality
