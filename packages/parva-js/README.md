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
const capabilities = await parva.getFutureBsCapabilities();
```

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
