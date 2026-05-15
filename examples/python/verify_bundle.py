from __future__ import annotations

import json
import os

from parva import ParvaClient

client = ParvaClient(base_url=os.environ.get("PARVA_API_BASE", "https://api.prabinghimire1.com.np/v3/api"))

payload = {
    "policy": client.get_policy(),
    "trust": client.get_trust_capabilities(),
    "future_bs_capabilities": client.get_future_bs_capabilities(),
}

print(json.dumps(payload, indent=2, sort_keys=True))
