# Parva Temporal Spec v1.0 (Normative Core)

Status: Draft (Normative Core)  
Scope: Nepali temporal computation baseline

## 1. Scope
This core spec defines normative behavior for:
1. Bikram Sambat boundary/conversion behavior.
2. Udaya tithi (tithi at local sunrise).
3. Adhik Maas classification.
4. Conformance obligations.

## 2. Conformance terms
`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are normative.

## 3. Canonical temporal model
1. Inputs MUST accept Gregorian dates as `YYYY-MM-DD`.
2. Astronomical calculations MUST run in UTC.
3. Daily tithi used for observance MUST be determined at local sunrise.
4. If location is missing/invalid, implementation MAY fallback to Kathmandu and MUST report warning metadata.

## 4. BS conversion (normative)
1. Implementations MUST return confidence classes: `official|computed|estimated`.
2. Implementations MUST return deterministic output for identical input and identical snapshot/rule context.
3. Outputs SHOULD include source range and estimated error metadata when applicable.

## 5. Udaya tithi (normative)
At local sunrise:

`elongation = (lambda_moon - lambda_sun) mod 360`

`absolute_tithi = floor(elongation / 12) + 1`  (1..30)

Mapping:
1. `1..15` => `paksha = shukla`, `display_tithi = absolute_tithi`
2. `16..30` => `paksha = krishna`, `display_tithi = absolute_tithi - 15`

Required output fields:
1. tithi number + display number
2. paksha
3. method
4. sunrise reference timestamp

## 6. Adhik Maas (normative)
1. Lunar month windows MUST be bounded by consecutive Amavasya instants.
2. A window MUST be `adhik` if no solar sankranti crossing occurs inside that window.
3. Classification MUST be deterministic for fixed ephemeris mode + ayanamsa configuration.

## 7. Conformance clauses
Conformance case pack:
- `/Users/rohanbasnet14/Documents/Project_Parva/tests/conformance/conformance_cases.v1.json`

Conformance runner:
- `/Users/rohanbasnet14/Documents/Project_Parva/scripts/spec/run_conformance_tests.py`

Pass criteria:
1. All mandatory cases return HTTP 200.
2. All required keys for each case are present.
3. Report shows 100% pass for mandatory set.

Report artifact:
- `/Users/rohanbasnet14/Documents/Project_Parva/reports/conformance_report.json`

## 8. Public API profile for this spec
Public compatibility profile is v3:
- `/v3/api/*`
- `/api/*` alias

Experimental tracks are non-normative and disabled by default.
