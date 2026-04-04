#!/usr/bin/env python3
"""Generate a scoped API key record for partner/commercial reads."""

from __future__ import annotations

import argparse
import json
import secrets
from dataclasses import dataclass

DEFAULT_SCOPES = ("commercial.read", "public.read")


@dataclass(frozen=True)
class PartnerKeyRecord:
    key_id: str
    secret: str
    scopes: tuple[str, ...]

    def env_entry(self) -> str:
        return f"{self.key_id}:{self.secret}:{'|'.join(self.scopes)}"

    def as_dict(self) -> dict[str, object]:
        return {
            "key_id": self.key_id,
            "secret": self.secret,
            "scopes": list(self.scopes),
            "parva_api_keys_entry": self.env_entry(),
            "curl_header": f"X-API-Key: {self.secret}",
        }


def _normalize_scopes(raw_scopes: str) -> tuple[str, ...]:
    scopes = tuple(scope.strip() for scope in raw_scopes.split(",") if scope.strip())
    if not scopes:
        raise ValueError("At least one scope is required.")
    return scopes


def generate_record(*, key_id: str, scopes: tuple[str, ...], bytes_length: int) -> PartnerKeyRecord:
    if not key_id.strip():
        raise ValueError("key_id must not be empty.")
    if bytes_length < 16:
        raise ValueError("bytes_length must be at least 16 for a production-facing key.")
    secret = secrets.token_urlsafe(bytes_length)
    return PartnerKeyRecord(key_id=key_id.strip(), secret=secret, scopes=scopes)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a partner API key entry for PARVA_API_KEYS.")
    parser.add_argument("--key-id", required=True, help="Stable identifier, e.g. municipality-kathmandu-prod.")
    parser.add_argument(
        "--scopes",
        default=",".join(DEFAULT_SCOPES),
        help="Comma-separated scopes, default: commercial.read,public.read",
    )
    parser.add_argument(
        "--bytes",
        type=int,
        default=24,
        help="Random secret byte count before URL-safe encoding. Default: 24",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of the human-readable summary.",
    )
    args = parser.parse_args()

    record = generate_record(
        key_id=args.key_id,
        scopes=_normalize_scopes(args.scopes),
        bytes_length=args.bytes,
    )

    if args.json:
        print(json.dumps(record.as_dict(), indent=2))
        return 0

    print("Generated Project Parva partner API key")
    print(f"Key ID: {record.key_id}")
    print(f"Scopes: {', '.join(record.scopes)}")
    print(f"Secret: {record.secret}")
    print("")
    print("PARVA_API_KEYS entry:")
    print(record.env_entry())
    print("")
    print("Example header:")
    print(f"X-API-Key: {record.secret}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
