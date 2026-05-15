from __future__ import annotations

import json
import os

from parva import ParvaClient

client = ParvaClient(base_url=os.environ.get("PARVA_API_BASE", "https://api.prabinghimire1.com.np/v3/api"))

payload = {
    "ad_to_bs": client.ad_to_bs("2026-04-14"),
    "bs_to_ad": client.bs_to_ad(2083, 1, 1),
}

print(json.dumps(payload, indent=2, sort_keys=True))
