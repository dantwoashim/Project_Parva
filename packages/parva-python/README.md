# Parva Python SDK Alpha

Public-safe Python SDK for Project Parva calendar APIs.

This alpha package uses the stable public calendar surface and the public future-BS capabilities summary. It does not call private future-BS prediction, export, model-run, backtest, comparison, corrected-value, or schedule-impact endpoints.

## Install

From this repository:

```bash
python -m pip install -e packages/parva-python
```

## Quick Start

```python
from parva import ParvaClient

client = ParvaClient()

today = client.get_today()
ad_to_bs = client.ad_to_bs("2026-04-14")
bs_to_ad = client.bs_to_ad(2083, 1, 1)
validation = client.validate_bs_date(2083, 1, 32)
capabilities = client.get_future_bs_capabilities()
```

## API Base

Default public API base:

```text
https://api.prabinghimire1.com.np/v3/api
```

Future-BS capabilities endpoint:

```text
https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities
```

Private deployments can override both values:

```python
client = ParvaClient(
    base_url="https://calendar.example.com/v3/api",
    future_bs_capabilities_url="https://calendar.example.com/v4/api/future-bs/capabilities",
)
```

## Claim Boundary

Future-BS capabilities describe a research surface. They are not official calendar publication and must preserve:

```text
computed_prediction_not_official
```
