# Parva Panchanga Proof v1

Panchanga proof artifacts are method-docketed membranes for computed almanac
components. They are replayable from pinned query inputs, method dockets, and
ephemeris metadata or fixtures.

Every Panchanga proof membrane includes:

- canonical query with date, location, timezone, ephemeris provider, fixture or
  kernel reference, ayanamsa, sidereal mode, and sunrise rule
- identity hash
- witness hash
- result fields for sunrise, sunset, tithi, nakshatra, yoga, karana, paksha,
  vara, sun, and moon
- field provenance for every result field
- method docket references
- ephemeris metadata
- proof-pack replay steps
- boundary vector with `not_panchanga_authority` and
  `not_ritual_final_authority`

Verification must replay the Panchanga result or validate it against a pinned
fixture. A wrong-but-self-consistent membrane must fail.
