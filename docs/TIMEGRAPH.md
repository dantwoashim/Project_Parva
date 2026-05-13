# Parva TimeGraph

Parva TimeGraph is a public-safe temporal knowledge graph for Project Parva.
It connects calendar facts, sources, releases, compliance profiles, decisions,
evidence packets, and conflicts so an answer can be traced instead of treated
as an isolated JSON value.

TimeGraph is audit support. It is not an official government calendar
publication and it is not legal, tax, payroll, banking-contract, or regulatory
authority.

## What It Answers

TimeGraph is designed to answer questions such as:

- Which facts support this calendar answer?
- Which sources support this fact?
- Which release contains this fact?
- Which profile depends on this fact?
- Which decisions were derived from this fact?
- Which evidence packet references this fact?
- Which facts conflict or require review?

## Public Graph Scope

The public graph is built from public Project Parva artifacts:

- public source registry
- public release manifest
- public trust log
- public BS/AD conversion corpus within the demo release coverage
- public fiscal and compliance profile logic where enabled

Private source archives, unpublished client data, full future month-length
vectors, private model runs, and corrected future values are not part of the
public graph.

RuleLang execution can reference TimeGraph fact ids where available. Rule traces may include BS/AD mapping facts, month-length facts, fiscal-period facts, profile policy facts, and working-day decision facts. If TimeGraph is unavailable, RuleLang degrades with a warning instead of inventing fact ids.

## Fact Model

A temporal fact contains:

- stable `fact_id`
- `fact_type`
- `subject`
- `predicate`
- `object`
- `source_ids`
- `release_id`
- `confidence`
- `claim_boundary`
- `warnings`
- optional jurisdiction, profile, validity, and metadata fields

Example fact ids:

```text
fact_bs_ad_2083_01_01
fact_ad_bs_2026_04_14
fact_month_length_bs_2082_01
fact_weekday_ad_2026_04_14
fact_fiscal_period_bs_2082_04_02
```

Fact ids are deterministic where practical.

## Relationships

Relationships connect facts to sources, releases, profiles, and derivations.

Common relationship types include:

- `SUPPORTED_BY`
- `CONTRADICTED_BY`
- `APPLIES_TO`
- `DERIVED_FROM`
- `COMPUTED_FROM`
- `BELONGS_TO`
- `PINNED_TO_RELEASE`
- `CONTAINS_FACT`
- `REFERENCES_FACT`
- `REQUIRES_REVIEW`

See [TIMEGRAPH_FACTS.md](TIMEGRAPH_FACTS.md) for the fact and relationship
catalog.

## Public Endpoints

The public TimeGraph API is bounded and read-only:

- `GET /v3/api/timegraph/capabilities`
- `GET /v3/api/timegraph/facts`
- `GET /v3/api/timegraph/facts/{fact_id}`
- `POST /v3/api/timegraph/query`
- `GET /v3/api/timegraph/date/{calendar}/{date_value}`
- `GET /v3/api/timegraph/sources/{source_id}/facts`
- `GET /v3/api/timegraph/releases/{release_id}/facts`
- `GET /v3/api/timegraph/profiles/{profile_id}/facts`
- `GET /v3/api/timegraph/entities/{entity_id}/relationships`
- `GET /v3/api/timegraph/facts/{fact_id}/trace`
- `GET /v3/api/timegraph/conflicts`

See [TIMEGRAPH_API.md](TIMEGRAPH_API.md) for examples.

## Trace Behavior

Fact traces return the fact, supporting sources, release metadata,
relationships, derived-from facts, evidence packets where available, conflicts,
warnings, confidence, and claim boundary.

Trace depth is bounded to keep public queries safe and predictable.

## Conflict Behavior

Conflicts are first-class graph objects. If a public graph conflict is only a
fixture, it is explicitly labeled as fixture-only and must not be treated as a
real source disagreement.

See [TIMEGRAPH_CONFLICTS.md](TIMEGRAPH_CONFLICTS.md).

## Limitations

- TimeGraph does not create official calendar authority.
- It only represents facts supported by public artifacts in public mode.
- It does not expose private source archives or private future-BS outputs.
- Fixture conflicts are for schema and workflow testing only.
- Future-BS research remains `computed_prediction_not_official`.

## Layer 7 Preparation

TimeGraph prepares Project Parva for a future rule layer by making temporal
claims explicit, source-linked, release-linked, traceable, and conflict-aware.
It does not implement that rule language itself.
