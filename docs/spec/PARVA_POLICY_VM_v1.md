# PARVA_POLICY_VM v1

The policy VM selects among candidate claims without mutating canonical truth.
It must emit:

- selected candidate
- rejected candidates and reasons
- decision trace
- derived boundary vector

Static lookup data is compatibility/reference data unless the request
explicitly asks for that branch or for a comparison membrane. Policy lenses may
project task-specific views, but overlays and lenses never rewrite canonical
claims.
