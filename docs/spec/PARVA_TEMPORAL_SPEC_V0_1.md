# Parva Temporal Specification v0.1

Status: early public draft
Scope: public temporal contracts for Project Parva
Audience: API consumers, SDK authors, integrators, and reviewers

Project Parva is source-aware Nepali temporal infrastructure for BS/AD conversion, fiscal-year logic, panchanga computation, festivals, calendar validation, and controlled future-BS risk research.

This draft defines shared names, field shapes, and claim boundaries. It is not a full implementation specification and it does not publish official future BS dates.

## 1. Conformance Language

The words `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are used with their ordinary technical meaning.

A Parva-compatible implementation SHOULD:

1. Return deterministic output for the same inputs, release, and source policy.
2. Include source policy and publication status wherever the result could be confused with an official or reviewed source.
3. Preserve the distinction between published evidence, computed output, and review-only signals.
4. Avoid treating weak third-party or software-table references as official proof.

## 2. Claim Boundary

Project Parva is not an official government calendar publication.

Official publication overrides computed output.

Future-BS research outputs MUST use:

```text
computed_prediction_not_official
```

Future-BS risk results are intended for validation, comparison, review routing, and operational risk detection. They are not legal, tax, regulatory, or banking-contract final authority.

## 3. Shared Enumerations

### Publication Status

`publication_status` MUST be one of:

- `official_verified`
- `printed_verified`
- `public_witness`
- `publisher_reference`
- `software_table_reference`
- `third_party_reference`
- `needs_review`
- `computed_prediction_not_official`

These values describe the claim posture of a value or record. Implementations MAY add separate internal source-tier metadata, but public contracts SHOULD preserve this enum for interoperability.

### Source Policy

`source_policy` SHOULD be one of:

- `official_strict`
- `printed_reviewed`
- `public_witness`
- `publisher_reference`
- `software_table_reference`
- `third_party_reference`
- `experimental_shadow`
- `public_demo`

An implementation MAY use a more specific internal policy name, but it MUST NOT imply official authority unless the source evidence supports that claim.

### Risk Label

`risk_label` MUST be one of:

- `GREEN`
- `YELLOW`
- `RED`

Risk labels describe review posture. They do not turn computed future output into official publication.

## 4. Core Data Concepts

### 4.1 PlainBSDate

A plain Bikram Sambat calendar date.

Fields:

- `calendar`: MUST be `BS`.
- `year`: integer BS year.
- `month`: integer month, 1 through 12.
- `day`: integer day, normally 1 through 32.
- `publication_status`: publication status enum.
- `source_policy`: source policy string.
- `release_id`: optional release identifier.

Example:

```json
{
  "calendar": "BS",
  "year": 2080,
  "month": 1,
  "day": 1,
  "publication_status": "official_verified",
  "source_policy": "official_strict",
  "release_id": "published-bs-2080"
}
```

### 4.2 PlainADDate

A plain Gregorian date used by Parva API contracts.

Fields:

- `calendar`: MUST be `AD`.
- `date`: Gregorian date in `YYYY-MM-DD` format.
- `timezone`: optional IANA timezone.
- `projection`: optional projection flag for values outside a published range.

Example:

```json
{
  "calendar": "AD",
  "date": "2023-04-14",
  "timezone": "Asia/Kathmandu",
  "projection": false
}
```

### 4.3 BSYearMonth

A BS year/month pair.

Fields:

- `year`: integer BS year.
- `month`: integer month, 1 through 12.
- `month_name`: optional display name.
- `release_id`: optional release identifier.

Example:

```json
{
  "year": 2080,
  "month": 1,
  "month_name": "Baisakh",
  "release_id": "published-bs-2080"
}
```

### 4.4 BSMonthStart

The AD date on which a BS month begins.

Fields:

- `bs_year`: integer BS year.
- `bs_month`: integer BS month, 1 through 12.
- `start_ad`: Gregorian date in `YYYY-MM-DD` format.
- `publication_status`: publication status enum.
- `source_refs`: array of `SourceRef` records or source identifiers.
- `source_policy`: source policy string.

Example:

```json
{
  "bs_year": 2080,
  "bs_month": 1,
  "start_ad": "2023-04-14",
  "publication_status": "official_verified",
  "source_refs": ["np-public-calendar-2080"],
  "source_policy": "official_strict"
}
```

## 5. Release And Evidence Concepts

### 5.1 CalendarRelease

A signed or versioned calendar dataset release.

Fields:

- `release_id`: stable release identifier.
- `calendar`: calendar name, such as `BS`.
- `coverage`: object describing covered years, months, or date ranges.
- `source_policy`: source policy string.
- `artifact_hashes`: object mapping artifact names to hashes.
- `publication_status`: publication status enum.
- `generated_at`: ISO 8601 timestamp.
- `previous_release`: optional previous release identifier.

### 5.2 SourceRef

A source reference used to explain where a value came from.

Fields:

- `source_id`: stable source identifier.
- `source_name`: human-readable source name.
- `source_tier`: source tier enum.
- `url`: optional public URL.
- `archive_ref`: optional archive or file reference.
- `reviewed_by`: optional reviewer identifier.
- `reviewed_at`: optional ISO 8601 timestamp.

### 5.3 CalculationTrace

An auditable trace for a conversion, panchanga computation, risk assessment, or reconciliation.

Fields:

- `trace_id`: stable trace identifier.
- `operation`: operation name.
- `input`: input object.
- `output`: output object.
- `release_id`: release identifier used by the calculation.
- `source_policy`: source policy string.
- `steps`: ordered calculation steps.
- `warnings`: warnings array.
- `publication_status`: publication status enum.

## 6. Domain Concepts

### 6.1 NepalFiscalYear

A Nepali fiscal year boundary record.

Fields:

- `label`: fiscal year label.
- `start_bs`: `PlainBSDate`.
- `end_bs`: `PlainBSDate`.
- `start_ad`: `PlainADDate`.
- `end_ad`: `PlainADDate`.
- `source_policy`: source policy string.
- `publication_status`: publication status enum.

### 6.2 FutureBSRiskAssessment

A future BS month risk posture, without exposing corrected future values by default.

Fields:

- `bs_year`: integer BS year.
- `bs_month`: integer BS month, 1 through 12.
- `publication_status`: MUST be `computed_prediction_not_official`.
- `risk_label`: `GREEN`, `YELLOW`, or `RED`.
- `corrected_value_included`: boolean.
- `reason_codes`: array of reason-code strings.
- `source_policy`: source policy string.
- `trace_id`: optional calculation trace identifier.

Public risk assessment examples MUST NOT include full future month-length vectors.

### 6.3 FestivalOccurrence

A dated festival occurrence.

Fields:

- `festival_id`: stable festival identifier.
- `name`: display name.
- `bs_date`: optional `PlainBSDate`.
- `ad_date`: optional `PlainADDate`.
- `rule_id`: rule identifier.
- `source_policy`: source policy string.
- `publication_status`: publication status enum.

### 6.4 PanchangaDay

A place-aware panchanga day summary.

Fields:

- `date`: `PlainADDate` or compatible date object.
- `place`: place label.
- `timezone`: IANA timezone.
- `tithi`: optional tithi display value.
- `paksha`: optional paksha display value.
- `nakshatra`: optional nakshatra display value.
- `yoga`: optional yoga display value.
- `karana`: optional karana display value.
- `sunrise`: optional local time or timestamp.
- `sunset`: optional local time or timestamp.
- `calculation_source`: calculation source description.
- `publication_status`: publication status enum.

### 6.5 ReconciliationEvent

An event emitted during controlled calendar reconciliation.

Fields:

- `event`: event type string.
- `release_version`: release version string.
- `affected_years`: array of BS years.
- `affected_months`: array of BS year/month strings.
- `requires_review`: boolean.
- `diff_available`: boolean.
- `publication_status`: publication status enum.
- `signature`: optional signature or signing reference.

Reconciliation events are for controlled workflows. They MUST NOT silently update production systems without an operator approval policy.

## 7. Schema Files

The v0.1 schema set is stored at the repository root under `schemas/`:

- `schemas/parva-date.schema.json`
- `schemas/calendar-release.schema.json`
- `schemas/source-ref.schema.json`
- `schemas/calculation-trace.schema.json`
- `schemas/future-risk.schema.json`
- `schemas/reconciliation-event.schema.json`
- `schemas/festival-occurrence.schema.json`
- `schemas/panchanga-day.schema.json`
- `schemas/nepal-fiscal-year.schema.json`

Schemas use JSON Schema draft 2020-12 style and include public-safe examples.

## 8. Versioning Notes

This is v0.1 and intentionally conservative.

Future versions may:

1. Split public schemas from private deployment schemas.
2. Add conformance case packs.
3. Add stronger release signing requirements.
4. Add SDK compatibility profiles.
5. Add formal source-policy profiles.

Any future version MUST preserve the claim boundary for computed future-BS output unless the governing source evidence changes.
