# Calendar Model-Risk Architecture

The additive model-risk layer sits on top of existing Parva calendar infrastructure.

Core layers:

- existing BS/AD, fiscal, holiday, panchanga, frontend, SDK, and deployment surfaces,
- private future BS prediction artifacts,
- source trust and corpus readiness,
- prediction sets and perturbation robustness,
- committee/civil-rule posterior,
- external sheet audit,
- schedule-impact analysis,
- claim readiness and red-team reports.

The public API surface is limited to capability metadata. Direct prediction, report, audit, and schedule-impact endpoints are private deployment surfaces and should not appear in public OpenAPI output.
