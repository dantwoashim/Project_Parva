# SDK Usage

Project Parva SDKs are alpha developer surfaces for stable public calendar APIs and the public future-BS capabilities summary.

They are intended for teams that want a cleaner integration path than raw HTTP calls while preserving source policy and claim boundaries.

## JavaScript and TypeScript

Install from a package release when available:

```bash
npm install @project-parva/parva-js
```

Local repository development:

```bash
npm --prefix packages/parva-js install
npm --prefix packages/parva-js test
npm --prefix packages/parva-js run build
```

Example:

```ts
import { ParvaClient } from "@project-parva/parva-js";

const parva = new ParvaClient();

const today = await parva.getToday();
const adToBs = await parva.adToBs("2026-04-14");
const bsToAd = await parva.bsToAd({ year: 2083, month: 1, day: 1 });
const validation = await parva.validateBsDate({ year: 2083, month: 1, day: 32 });
const futureBsCapabilities = await parva.getFutureBsCapabilities();
```

## Python

Install from the repository:

```bash
python -m pip install -e packages/parva-python
```

Example:

```python
from parva import ParvaClient

parva = ParvaClient()

today = parva.get_today()
ad_to_bs = parva.ad_to_bs("2026-04-14")
bs_to_ad = parva.bs_to_ad(2083, 1, 1)
validation = parva.validate_bs_date(2083, 1, 32)
future_bs_capabilities = parva.get_future_bs_capabilities()
```

## CLI

Run from the repository root:

```bash
python tools/parva-cli/parva_cli.py --help
python tools/parva-cli/parva_cli.py today
python tools/parva-cli/parva_cli.py convert ad 2026-04-14
python tools/parva-cli/parva_cli.py convert bs 2083-01-01
python tools/parva-cli/parva_cli.py validate bs 2083-01-32
python tools/parva-cli/parva_cli.py capabilities future-bs
```

## API Base Configuration

Default public API base:

```text
https://api.prabinghimire1.com.np/v3/api
```

Future-BS capabilities endpoint:

```text
https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities
```

Private deployments may override these values, but public SDK examples must stay on stable public surfaces.

## Public and Private Boundary

Public SDK methods in this alpha:

- `getToday` or `get_today`
- `adToBs` or `ad_to_bs`
- `bsToAd` or `bs_to_ad`
- `validateBsDate` or `validate_bs_date`
- `getFutureBsCapabilities` or `get_future_bs_capabilities`

The SDKs do not call private future-BS month-length prediction, full-range export, model-run, backtest, residual, external comparison, corrected-value, or schedule-impact endpoints.

## Future-BS Claim Boundary

The future-BS SDK method returns capability metadata only. It must not be treated as official publication authority.

Any future-BS output exposed through public SDKs must preserve:

```text
computed_prediction_not_official
```

Official publication overrides computed output.

## Conformance Path

The SDKs should use the repository conformance suite as the baseline compatibility target:

```bash
python tools/conformance_runner/run.py
```

Future SDK work should add language-specific conformance adapters that load the JSON cases under `conformance/` and compare SDK outputs against the same public-safe cases.

## Release And Trace Metadata

API responses may include optional metadata such as `release_id`, `calculation_trace_id`, `source_policy`, or `publication_status`.

SDK consumers should preserve this metadata when storing or forwarding calendar results. A release identifier explains which public artifact set was used. A trace identifier explains which calculation steps produced the result.

Future-BS metadata still remains:

```text
computed_prediction_not_official
```
