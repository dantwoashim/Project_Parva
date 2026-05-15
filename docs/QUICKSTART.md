---
status: stable
audience: developer
---

# Quickstart

Project Parva is source-backed Nepali time infrastructure for software systems.
It provides deterministic BS/AD conversion, fiscal-year logic, working-day
helpers, public-safe trust metadata, and review-gated preview surfaces.

Parva is not a government authority, legal authority, tax advisor,
banking-contract authority, payroll final authority, or religious authority.
Official institutions remain authoritative for their own publications.

## 1. Check the Toolchain

Backend work requires Python 3.11.x. Frontend and JS SDK work require Node 20.x.

Linux/macOS:

```bash
python3.11 --version
node --version
python3.11 scripts/verify_environment.py
```

Windows PowerShell:

```powershell
$env:PATH="C:\Users\<you>\AppData\Local\Programs\Python\Python311;C:\Users\<you>\AppData\Local\Programs\Python\Python311\Scripts;" + $env:PATH
python --version
node --version
python scripts/verify_environment.py
```

## 2. Install

```bash
python -m pip install -e .[test,dev]
python -m pip install -e packages/parva-python
npm --prefix packages/parva-js ci
```

## 3. Call Stable Public Routes

REST base:

```text
https://api.prabinghimire1.com.np/v3/api
```

AD to BS:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/convert?date=2026-04-14"
```

BS to AD:

```bash
curl -X POST "https://api.prabinghimire1.com.np/v3/api/calendar/bs-to-gregorian" \
  -H "Content-Type: application/json" \
  -d '{"year":2083,"month":1,"day":1}'
```

Fiscal year:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/enterprise/fiscal-year/2082"
```

Working day:

```bash
curl -X POST "https://api.prabinghimire1.com.np/v3/api/compliance/next-working-day" \
  -H "Content-Type: application/json" \
  -d '{"profile_id":"nepal_private_company_default","bs_date":"2082-04-02"}'
```

Trust/source metadata:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/trust/sources"
```

## 4. Python SDK

```python
from parva import ParvaClient

client = ParvaClient(base_url="https://api.prabinghimire1.com.np/v3/api")

ad_to_bs = client.ad_to_bs("2026-04-14")
bs_to_ad = client.bs_to_ad(2083, 1, 1)
fiscal = client.get_fiscal_year(2082)
working_day = client.next_working_day(
    profile_id="nepal_private_company_default",
    bs_date="2082-04-02",
)
sources = client.list_sources()
capabilities = client.get_future_bs_capabilities()

print(ad_to_bs)
print(bs_to_ad)
print(fiscal)
print(working_day)
print(sources.get("items") or sources)
print(capabilities.get("publication_status"))
```

## 5. JavaScript SDK

```ts
import { ParvaClient } from "@project-parva/parva-js";

const parva = new ParvaClient({
  baseUrl: "https://api.prabinghimire1.com.np/v3/api",
});

const adToBs = await parva.adToBs("2026-04-14");
const bsToAd = await parva.bsToAd({ year: 2083, month: 1, day: 1 });
const fiscalYear = await parva.getFiscalYear(2082);
const workingDay = await parva.nextWorkingDay({
  profile_id: "nepal_private_company_default",
  bs_date: "2082-04-02",
});
const sources = await parva.listSources();
const capabilities = await parva.getFutureBsCapabilities();
```

## 6. Handle Review and Error Boundaries

Stable public responses may include source, confidence, maturity, warning, or
claim-boundary metadata depending on the route. Treat these as part of the
contract. If a response says `review_required`, `unsupported`, or
`computed_prediction_not_official`, do not automate a final legal, tax, payroll,
banking, or religious decision from it.

Private Future-BS prediction, export, model-run, backtest, comparison, and
schedule-impact routes are intentionally not quickstart routes. Use only the
public capabilities endpoint unless you are operating a private research
deployment with explicit gates and human review.

## 7. Verify

```bash
python scripts/check_future_bs_public_leakage.py
python scripts/release/verify_public.py
```
