from __future__ import annotations

import json

from parva import ParvaClient
from preflight import resolve_api_base

client = ParvaClient(base_url=resolve_api_base())

payload = {
    "policy": client.get_policy(),
    "trust": client.get_trust_capabilities(),
    "future_bs_capabilities": client.get_future_bs_capabilities(),
}

print(json.dumps(payload, indent=2, sort_keys=True))
