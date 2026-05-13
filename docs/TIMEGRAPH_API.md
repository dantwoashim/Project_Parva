# TimeGraph API

The TimeGraph API exposes bounded, public-safe graph queries for temporal facts,
relationships, traces, and conflicts.

Base URL:

```text
https://api.prabinghimire1.com.np/v3/api
```

## Capabilities

```bash
curl https://api.prabinghimire1.com.np/v3/api/timegraph/capabilities
```

The response describes public graph scope, supported fact types, relationship
types, query limits, claim boundary, and warnings.

## List Facts

```bash
curl "https://api.prabinghimire1.com.np/v3/api/timegraph/facts?fact_type=bs_ad_mapping&limit=5"
```

Supported filters include:

- `fact_type`
- `date`
- `calendar`
- `source_id`
- `release_id`
- `profile_id`
- `confidence`
- `claim_boundary`
- `jurisdiction`
- `has_conflicts`
- `limit`
- `offset`

Queries are bounded. The default limit is small and the maximum public limit is
enforced by the API.

## Get A Fact

```bash
curl https://api.prabinghimire1.com.np/v3/api/timegraph/facts/fact_bs_ad_2083_01_01
```

The response includes the fact, direct relationships, and metadata.

## Query Facts

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/timegraph/query \
  -H "Content-Type: application/json" \
  -d '{"calendar":"BS","date":"2083-01-01","limit":5}'
```

## Date Query

```bash
curl https://api.prabinghimire1.com.np/v3/api/timegraph/date/BS/2083-01-01
```

This returns facts for a BS or AD date. Use `BS` or `AD` as the calendar path
segment.

## Source Query

```bash
curl https://api.prabinghimire1.com.np/v3/api/timegraph/sources/parva_public_bs_ad_corpus/facts
```

## Release Query

```bash
curl https://api.prabinghimire1.com.np/v3/api/timegraph/releases/parva-bs-public-demo/facts
```

## Profile Query

```bash
curl https://api.prabinghimire1.com.np/v3/api/timegraph/profiles/nepal_private_company_default/facts
```

## Relationships

```bash
curl https://api.prabinghimire1.com.np/v3/api/timegraph/entities/fact_bs_ad_2083_01_01/relationships
```

## Trace A Fact

```bash
curl "https://api.prabinghimire1.com.np/v3/api/timegraph/facts/fact_bs_ad_2083_01_01/trace?depth=2"
```

Trace responses include:

- fact
- sources
- release
- derived-from facts
- relationships
- evidence packets where available
- conflicts
- confidence
- warnings
- claim boundary

Trace depth is bounded.

## Conflicts

```bash
curl https://api.prabinghimire1.com.np/v3/api/timegraph/conflicts
```

Fixture conflicts are labeled fixture-only. Do not treat them as real source
disagreements.

## SDK Examples

JavaScript:

```ts
const parva = new ParvaClient();
const facts = await parva.getFactsForDate("BS", "2083-01-01", { limit: 5 });
const trace = await parva.traceFact("fact_bs_ad_2083_01_01", { depth: 2 });
```

Python:

```python
client = ParvaClient()
facts = client.get_facts_for_date("BS", "2083-01-01", limit=5)
trace = client.trace_fact("fact_bs_ad_2083_01_01", depth=2)
```

## Boundary

TimeGraph is audit support. It does not replace official publications or an
organization's own legal, tax, payroll, banking-contract, or compliance policy.
