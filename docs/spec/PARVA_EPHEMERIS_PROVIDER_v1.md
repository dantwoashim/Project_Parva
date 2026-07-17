# Parva Ephemeris Provider v1

Parva ephemeris providers are method-backed computation inputs, not public
authority sources.

Provider metadata must disclose:

- `provider_id`
- `provider_kind`
- ephemeris name/version
- kernel or fixture hash when applicable
- time scale
- coordinate frame
- precision/tolerance note
- supported date range
- method docket reference
- boundary vector

Supported provider classes:

- `builtin_swiss_moshier`: built-in Swiss/Moshier fallback approximation.
- `pinned_panchanga_fixture`: committed deterministic fixture slice for replay tests.

`jpl_de440` is reserved and cannot be selected as a Panchanga calculation
provider. The current JPL surface validates and discloses configured kernel
metadata only. It never labels Swiss/Moshier Panchanga output as JPL output.

No provider confers government, religious, ritual, legal, tax, payroll, banking,
or official Panchanga authority.
