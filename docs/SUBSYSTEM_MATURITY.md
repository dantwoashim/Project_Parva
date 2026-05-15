# Subsystem Maturity

Status: public exposure control.

Source of truth: [config/subsystem-maturity.yaml](../config/subsystem-maturity.yaml)

This document summarizes the maturity lanes used to decide which Project Parva
subsystems may be public, which must remain controlled, and which claims are
allowed for each subsystem.

## Lanes

| Lane | Public exposure | Meaning |
| --- | --- | --- |
| `stable_core` | Public | Core conversion, fiscal, and policy surfaces intended for integrations. |
| `public_preview` | Public or partial | Public-safe previews that require labels, metadata, and limits. |
| `developer_preview` | Partial | Developer-facing tools that may change and require explicit preview labeling. |
| `enterprise_preview` | Controlled | Billing, admin, customer, or compliance workflows that are not public demo surfaces. |
| `research_private` | Private | Research data, exact future outputs, and model artifacts. |
| `protocol_draft` | Public draft | Draft protocol, conformance, and schema work without standards claims. |
| `deprecated_compatibility` | Partial | Legacy aliases kept for existing clients with a sunset path. |
| `historical` | Docs only | Historical snapshots that do not prove current verification status. |

## Current Subsystem Map

| Subsystem | Lane | Public rule |
| --- | --- | --- |
| Core calendar, fiscal, working-day | `stable_core` | Public with source and claim-boundary metadata. |
| Panchanga, tithi, festivals, holidays, muhurta, kundali | `public_preview` | Public-safe only with method, confidence, and non-authority labels. |
| Trust, source registry, release manifests, evidence packets | `public_preview` | Public metadata only. Private evidence and unpublished paths stay out of public profiles. |
| TimeGraph, RuleLang, impact simulator, agent tools | `developer_preview` | Developer preview routes, bounded samples, and no legal or payroll authority claims. |
| Parva Protocol, conformance, credentials | `protocol_draft` | Draft protocol only. No standards, certification, or government endorsement claim. |
| Future BS research | `research_private` | Public metadata and risk language only. Exact predictions and artifacts are private. |
| Frontend, embeds, SDKs, docs | `public_preview` | Capability-aware public reference surfaces with clear maturity labels. |
| Billing, API keys, admin | `enterprise_preview` | Controlled profile only and not part of the public demo. |

## Acceptance Rules

- Every subsystem in the registry must name a lane, maturity value, route
  profile exposure, CI gate, docs, allowed claims, and forbidden claims.
- A subsystem may not be marketed above its lane.
- Future-BS exact outputs remain private and labeled:

```text
publication_status = computed_prediction_not_official
```

- Historical and internal-audit docs must be labeled as historical snapshots,
  not current verification proof.

