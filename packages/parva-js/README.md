# Parva JS SDK Alpha

Public-safe JavaScript and TypeScript SDK for Project Parva.

This alpha package targets stable public calendar APIs and the safe future-BS capabilities summary. It does not call private future-BS prediction, export, model-run, backtest, comparison, corrected-value, or schedule-impact endpoints.

## Install

```bash
npm install @project-parva/parva-js
```

For local repository development:

```bash
npm --prefix packages/parva-js install
npm --prefix packages/parva-js test
npm --prefix packages/parva-js run build
```

## Quick Start

```ts
import { ParvaClient } from "@project-parva/parva-js";

const parva = new ParvaClient();

const today = await parva.getToday();
const adToBs = await parva.adToBs("2026-04-14");
const bsToAd = await parva.bsToAd({ year: 2083, month: 1, day: 1 });
const validation = await parva.validateBsDate({ year: 2083, month: 1, day: 32 });
const month = await parva.getMonthCalendar(2026, 4);
const fiscalYear = await parva.getFiscalYear(2082);
const bsMonths = await parva.getBsMonths(2082);
const businessDays = await parva.getBusinessDays({
  start_bs: "2082-01-01",
  end_bs: "2082-01-07",
});
const enterprise = await parva.getEnterpriseCapabilities();
const compliance = await parva.evaluateDate({
  profile_id: "nepal_private_company_default",
  bs_date: "2082-04-02",
});
const trust = await parva.getTrustCapabilities();
const evidence = await parva.createDateConversionEvidence({
  ad_date: "2026-04-14",
});
const timegraph = await parva.getTimeGraphCapabilities();
const facts = await parva.getFactsForDate("BS", "2083-01-01");
const trace = await parva.traceFact("fact_bs_ad_2083_01_01");
const rule = await parva.evaluateRule("last_working_day_of_nepali_month", {
  input: { bs_month: "2082-04", profile_id: "nepal_private_company_default" },
});
const policy = await parva.getPolicy();
const capabilities = await parva.getFutureBsCapabilities();
```

## Covered Public Surfaces

- current calendar context
- AD to BS conversion
- BS to AD conversion
- BS date validation through conversion
- month calendar
- fiscal-year boundaries
- BS month metadata
- weekend-rule business-day helper
- enterprise capability metadata
- compliance profile listing and decision support helpers
- trust source, release, diff, log, and evidence packet helpers
- TimeGraph fact, relationship, trace, and conflict helpers
- RuleLang registry, validation, execution, test, and explanation helpers
- public policy metadata
- future-BS capabilities summary

## TimeGraph

TimeGraph helpers expose public-safe temporal facts and traces. They keep fact ids,
relationships, source ids, release ids, confidence, warnings, trace ids, and
conflict metadata intact.

```ts
const dateFacts = await parva.getFactsForDate("BS", "2083-01-01", { limit: 10 });
const fact = await parva.getFact("fact_bs_ad_2083_01_01");
const trace = await parva.traceFact("fact_bs_ad_2083_01_01", { depth: 2 });
const conflicts = await parva.listConflicts();
```

TimeGraph responses are audit support and not legal, tax, payroll, banking-contract,
or government authority.

## RuleLang

RuleLang helpers evaluate structured temporal rules with bounded execution, reason
codes, traces, metadata, and fact ids.

```ts
const rules = await parva.listRules();
const result = await parva.evaluateRule("last_working_day_of_nepali_month", {
  input: { bs_month: "2082-04", profile_id: "nepal_private_company_default" },
});
const explanation = await parva.explainRule({
  rule_id: "last_working_day_of_nepali_month",
  input: { bs_month: "2082-04", profile_id: "nepal_private_company_default" },
});
```

RuleLang is decision support and not legal, tax, payroll, banking-contract, or
government authority.

## API Base

The default public API base is:

```text
https://api.prabinghimire1.com.np/v3/api
```

The future-BS capabilities method uses the public v4 capabilities endpoint:

```text
https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities
```

You can override both for private deployments:

```ts
const parva = new ParvaClient({
  baseUrl: "https://calendar.example.com/v3/api",
  futureBsCapabilitiesUrl: "https://calendar.example.com/v4/api/future-bs/capabilities",
});
```

## Claim Boundary

Future-BS capability responses are metadata about a research layer. They are not official calendar publication and must preserve:

```text
computed_prediction_not_official
```
