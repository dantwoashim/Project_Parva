---
status: public-beta
tier: 1
lane: core
last_verified: 2026-07-20
owner: platform-team
---

# Agent API

Public preview endpoints:

- `GET /v3/api/agent/capabilities`
- `GET /v3/api/agent/tools`
- `GET /v3/api/agent/manifest`
- `POST /v3/api/agent/resolve-intent`
- `POST /v3/api/agent/verify-claim`
- `POST /v3/api/agent/plan-schedule`
- `POST /v3/api/agent/explain`
- `POST /v3/api/agent/check-human-review`
- `POST /v3/api/agent/draft-rule`
- `POST /v3/api/agent/run-tool`

The agent claim boundary is `agent_temporal_reasoning_not_legal_authority`.

`run-tool` is the single HTTP execution boundary used by the MCP server. Invalid
tool input returns a structured 4xx response with an agent error code.
