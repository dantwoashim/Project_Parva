#!/usr/bin/env python3
"""Generate the static public-demo OpenAPI artifact used by docs mirrors."""

from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "docs" / "api-docs" / "openapi.json"


def main() -> int:
    os.environ["PARVA_ROUTE_PROFILE"] = "public_demo"
    os.environ["PARVA_ENABLE_EXPERIMENTAL_API"] = "false"
    os.environ["PARVA_SHOW_PRIVATE_SCHEMA"] = "false"
    os.environ["PARVA_ENV"] = "public"
    os.environ["PARVA_SOURCE_URL"] = "https://github.com/dantwoashim/Project_Parva"
    os.environ["PARVA_REQUIRE_PRECOMPUTED"] = "false"
    os.environ["PARVA_SERVE_FRONTEND"] = "false"
    os.environ.setdefault("PARVA_RATE_LIMIT_ENABLED", "false")

    from app.bootstrap.app_factory import create_app

    app = create_app()
    schema = app.openapi()
    schema["servers"] = [
        {
            "url": os.getenv(
                "PARVA_PUBLIC_DEMO_SERVER",
                "https://project-parva-public-demo.onrender.com",
            ),
            "description": "Render public demo backend",
        }
    ]
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(PROJECT_ROOT)} with {len(schema.get('paths', {}))} paths.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
