#!/usr/bin/env python3
"""Smoke-test the packaged Python SDK import paths."""

from __future__ import annotations

import warnings


def main() -> int:
    import parva_sdk

    client = parva_sdk.ParvaClient("http://localhost:8000/v3/api")
    assert client.base_url == "http://localhost:8000/v3/api"

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        import parva

        legacy_client = parva.ParvaClient("http://localhost:8000/v3/api")
        assert legacy_client.base_url == "http://localhost:8000/v3/api"
        assert parva.ParvaError is not None

    if not any("deprecated" in str(item.message).lower() for item in caught):
        raise SystemExit("Expected legacy 'parva' import path to emit DeprecationWarning.")

    print("Python SDK package imports passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
