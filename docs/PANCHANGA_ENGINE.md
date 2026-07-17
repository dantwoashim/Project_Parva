# Panchanga Engine

Project Parva's Panchanga engine computes method-docketed Panchanga signals for
software systems. It does not replace official, traditional, religious, or
ritual authorities.

## Computed Components

- sunrise
- sunset
- tithi at sunrise
- nakshatra at sunrise
- yoga
- karana
- paksha
- weekday / vara
- sun and moon sidereal context

## Required Proof Inputs

Proof-mode Panchanga queries make defaults explicit:

- Gregorian date
- latitude and longitude
- timezone
- ephemeris provider
- fixture id or kernel metadata when applicable
- ayanamsa
- sidereal mode
- sunrise attribution rule
- policy id

## Ephemeris Providers

- `builtin_swiss_moshier`: built-in Swiss/Moshier fallback approximation.
- `pinned_panchanga_fixture`: committed deterministic fixture slice for tests
  and local replay.

The reserved `jpl_de440` calculation-provider id is rejected. A separately
configured DE440-family file can be validated for metadata inspection, but it
cannot produce Panchanga output through this provider surface.

The built-in provider supports `lahiri`, `raman`, and `kp` as immutable
request profiles. The selected profile is applied to the calculation under the
shared Swiss Ephemeris state lock, restored after the request, and reported as
`effective_ayanamsa` in proof metadata.

## Boundaries

Every serious Panchanga proof result must include:

- `computed_not_official`
- `not_panchanga_authority`
- `not_ritual_final_authority`
- `review_required`
- location/timezone sensitivity
- ephemeris/method dependency

For final ritual decisions, consult the appropriate traditional or institutional
authority.
