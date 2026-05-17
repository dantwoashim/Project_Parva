# Parva Panchanga Engine v1

The Panchanga engine computes Panchanga components for software and audit
workflows. It is not an official Panchanga, ritual authority, or religious
authority.

Core computed components:

- sunrise and sunset
- tithi at sunrise
- nakshatra at sunrise
- yoga
- karana
- paksha
- weekday / vara
- sun and moon sidereal context

The engine is location-sensitive, timezone-sensitive, ephemeris-dependent, and
ayanamsa-dependent. Hidden defaults are not allowed in proof mode; Kathmandu,
`Asia/Kathmandu`, Lahiri ayanamsa, and the selected ephemeris provider are all
explicit query inputs.

JPL support is an interface and configuration path. The repository does not
bundle large JPL kernels. Local deployments may configure a JPL DE440-family
kernel with `PARVA_JPL_DE440_KERNEL`; pinned fixture slices are used for
deterministic tests.
