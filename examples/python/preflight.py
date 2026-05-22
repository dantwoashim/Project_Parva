from __future__ import annotations

import os
import sys

DEFAULT_EXAMPLE_API_BASE = "https://api.prabinghimire1.com.np/v3/api"


def resolve_api_base() -> str:
    base_url = os.environ.get("PARVA_API_BASE", DEFAULT_EXAMPLE_API_BASE).rstrip("/")
    print(f"[parva-example] Using API base: {base_url}", file=sys.stderr)
    return base_url

