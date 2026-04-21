# Risk Register

| Risk | Why it matters | Current posture | Review trigger |
| --- | --- | --- | --- |
| Under-hardened deployment | A strong backend can still be deployed unsafely | Reduced by startup validation and production preflight, but still depends on operator discipline | every release |
| Alias/version confusion | `/api/*`, `/v2`, `/v4`, `/v5` can still be misread as equal contracts | Mitigated by docs and policy metadata | every docs/release review |
| Frontend mispositioning | Users can mistake the reference frontend for a fully productized app | Mitigated by docs and visible in-app labeling | every UX/release review |
| Provider privacy drift | Remote geocoding can leak more than an operator intends | Mitigated by explicit production provider policy | every deployment |
| Provenance mismatch | Release outputs can drift from the published source/story | Mitigated by source publication and provenance gates | every release |
| Typing and contract drift | Backend/frontend surfaces can drift without stronger typed contracts | Partially reduced by split client/contract modules; still an active improvement area | every API change |
