---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Reference Implementation Mapping

- PTS-001 date representation: `backend/app/calendar`, `backend/app/services/calendar_conversion_service.py`
- PTS-002 source registry: `data/public/releases/*.sources.json`, `backend/app/services/trust_infrastructure_service.py`
- PTS-004 release manifest: `data/public/releases/*.manifest.json`
- PTS-006 evidence packet: `backend/app/services/trust_infrastructure_service.py`
- PTS-008 TimeGraph: `backend/app/services/timegraph_service.py`
- PTS-009 RuleLang: `backend/app/services/rulelang_service.py`
- PTS-010 impact report: `backend/app/services/impact_service.py`
- PTS-011 agent tools: `backend/app/services/agent_service.py`
- PTS-012 credentials: `backend/app/services/protocol_service.py`
- PTS-013 conformance: `scripts/parva_conformance.py`
