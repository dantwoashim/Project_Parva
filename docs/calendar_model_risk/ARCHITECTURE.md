# Calendar Model-Risk Architecture

The additive model-risk layer sits on top of existing Parva calendar infrastructure.

Core layers:

- existing BS/AD, fiscal, holiday, panchanga, frontend, SDK, and deployment surfaces,
- future BS prediction artifacts,
- source trust and corpus readiness,
- prediction sets and perturbation robustness,
- committee/civil-rule posterior,
- external sheet audit,
- Calendar VaR,
- claim readiness and red-team reports.

The API surface is `/v5/api/calendar-model-risk/*`.
