---
status: public-beta
audience: enterprise
---

# Temporal SBOM Service

A temporal SBOM records which calendar rules, source tiers, route versions, and
review gates a software system depends on.

Minimum inventory:

- BS/AD conversion route version,
- fiscal-year and working-day policy,
- holiday and festival source policy,
- panchanga or tithi method when used,
- Future-BS boundary status,
- source registry release id,
- verification commands and timestamps.

The service supports vendor audits and private deployments. It does not certify
software, replace official publications, or create legal authority.

Vendor audit output should include a temporal SBOM section naming route
versions, source policy, holiday policy, fiscal assumptions, unsupported future
assumptions, and review-required cases. The SBOM is evidence for engineering
review, not proof of external certification.
