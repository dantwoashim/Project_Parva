from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.release.check_contract_freeze import _normalize
from scripts.release.openapi_normalization import normalized_openapi_json


def test_contract_normalization_drops_only_open_object_defaults() -> None:
    schema = {
        "components": {
            "schemas": {
                "Open": {"type": "object", "additionalProperties": True},
                "Closed": {"type": "object", "additionalProperties": False},
            }
        }
    }

    normalized = _normalize(schema)

    schemas = normalized["components"]["schemas"]
    assert "additionalProperties" not in schemas["Open"]
    assert schemas["Closed"]["additionalProperties"] is False


def test_openapi_file_normalization_treats_explicit_open_objects_as_default(tmp_path: Path) -> None:
    implicit = tmp_path / "implicit.json"
    explicit = tmp_path / "explicit.json"
    implicit.write_text('{"schema":{"type":"object"}}', encoding="utf-8")
    explicit.write_text(
        '{"schema":{"additionalProperties":true,"type":"object"}}',
        encoding="utf-8",
    )

    assert normalized_openapi_json(implicit) == normalized_openapi_json(explicit)


def test_v3_contract_snapshot_is_public_reference_only() -> None:
    snapshot_path = Path("docs/contracts/v3_openapi_snapshot.json")
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))

    assert payload["track"] == "v3"
    assert payload["route_profile"] == "public_reference"

    routes = set(payload["schema"]["paths"])
    assert routes
    assert all(route.startswith("/v3/") for route in routes)
    assert not any(
        re.search(r"/(?:admin|billing|private|research|internal)(?:/|$)", route)
        for route in routes
    )
