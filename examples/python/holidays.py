from __future__ import annotations

import json

from parva import ParvaClient
from preflight import resolve_api_base

client = ParvaClient(base_url=resolve_api_base())

payload = client.evaluate_date(
    profile_id="nepal_private_company_default",
    bs_date="2082-01-01",
    decision_intent="public_holiday_lookup",
)

print(json.dumps(payload, indent=2, sort_keys=True))
