# Parva Query Canonicalization v1

Canonical queries are sorted JSON objects with explicit defaults for calendar,
place, policy, community, locale, and timezone. Hidden defaults are forbidden.

Required fields:
- `canonicalization_version`
- `operation`
- `input`
- `context`

Equivalent surface forms, including Devanagari digits and supported aliases,
must normalize to the same identity hash. Policy and place changes must produce
different identity hashes.
