# Project Parva — Roadmap & Scope Boundaries

_Last updated: 2026-02-16_

## Shipped (v4.0.0)

| Feature | Status | Evidence |
|---------|--------|----------|
| Ephemeris-powered panchanga engine | ✅ Live | Swiss Ephemeris backbone |
| 453 festival rules (396 computed) | ✅ Live | 87.4% computed coverage |
| 100% accuracy benchmark | ✅ Live | 67 MoHA ground truth comparisons |
| Muhurta engine (30/day + Rahu Kalam) | ✅ Live | `/api/muhurta/*` |
| Personal Panchanga (any lat/lon) | ✅ Live | `/api/personal/*` |
| Kundali (birth chart) | ✅ Live | `/api/kundali/*` |
| Navagraha positions | ✅ Live | `/api/graha/*` |
| v2-v5 versioned APIs | ✅ Live | 24 routers × 5 prefixes |
| Rate limiter + health metrics | ✅ Live | 120 req/min, uptime tracking |
| SDK packages (Python/TS/Go) | ✅ Ready | Publish workflow in CI |

## Year 2+ Roadmap (Explicitly Not Shipped)

> [!IMPORTANT]
> The following features were in the original Master Plan but are **not part of the v4.0 delivery**.
> This is an honest scope boundary, not a failure.

### Community Layer
- **What**: User-contributed festival observations, voting, corrections
- **Why descoped**: Requires persistence model (database), moderation system, authentication — fundamentally different product surface
- **Prerequisite**: User base for the core product first

### AR/WebXR Layer
- **What**: Augmented reality festival discovery overlay
- **Why descoped**: Requires entirely new frontend module (WebXR API), 3D assets, device compatibility testing
- **Prerequisite**: Stable mobile-responsive frontend first

### Peer-Reviewed Publication
- **What**: Academic paper submitted to ACM/journal with independent replication
- **Why descoped**: Requires months of external review process, co-authors, institutional affiliation
- **Status**: Reproducibility package and conformance assets exist; paper authoring pending

### Institutional Asymmetric Signing
- **What**: HSM-backed signing of provenance records with external verifier ecosystem
- **Why descoped**: Requires key ceremony, PKI setup, third-party verifier contracts
- **Status**: Hash-based signatures present; institutional upgrade pending
