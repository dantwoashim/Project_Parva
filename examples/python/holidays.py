from __future__ import annotations

import json
import os

from parva import ParvaClient


client = ParvaClient(base_url=os.environ.get("PARVA_API_BASE", "https://api.prabinghimire1.com.np/v3/api"))

payload = client.evaluate_date(
    profile_id="nepal_private_company_default",
    bs_date="2082-01-01",
    decision_intent="public_holiday_lookup",
)

print(json.dumps(payload, indent=2, sort_keys=True))
