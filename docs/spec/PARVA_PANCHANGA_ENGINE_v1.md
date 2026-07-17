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

The repository does not bundle large JPL kernels. Local deployments may
validate a configured DE440-family file for metadata inspection, but the file
is not a selectable Panchanga calculation provider. Pinned fixture slices are
used for deterministic tests.
