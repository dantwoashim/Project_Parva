from __future__ import annotations

import json

from parva import ParvaClient
from preflight import resolve_api_base

client = ParvaClient(base_url=resolve_api_base())

payload = {
    "ad_to_bs": client.ad_to_bs("2026-04-14"),
    "bs_to_ad": client.bs_to_ad(2083, 1, 1),
}

print(json.dumps(payload, indent=2, sort_keys=True))
