#!/usr/bin/env python3
"""
Harvest decoded Ratopati calendar month data for a BS year range.

The Ratopati calendar frontend exposes a public API base at:
    https://calapp.ratopati.com/api

Those responses are AES-encrypted in transit but decrypted in the client with a
publicly exposed key in the app config. This script reproduces that client-side
decode step so the project can archive provider-derived historical event and
holiday data as a secondary cross-validation pool.

Outputs:
    - data/source_inventory/digital_calendar_providers.json
    - data/source_inventory/ratopati_month_coverage_<start>_<end>.json
    - data/source_archive/ratopati/event_days_<start>_<end>.json

Usage:
    python backend/tools/harvest_ratopati_calendar.py
    python backend/tools/harvest_ratopati_calendar.py --start-year 1990 --end-year 2100
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
SOURCE_INVENTORY_DIR = DATA_DIR / "source_inventory"
SOURCE_ARCHIVE_DIR = DATA_DIR / "source_archive" / "ratopati"

SOURCE_INVENTORY_DIR.mkdir(parents=True, exist_ok=True)
SOURCE_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

PROVIDER_INVENTORY_PATH = SOURCE_INVENTORY_DIR / "digital_calendar_providers.json"


@dataclass
class RatopatiConfig:
    api_base_url: str
    encryption_enabled: bool
    key: str
    homepage_url: str = "https://calendar.ratopati.com/ad"


class RatopatiHarvester:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://calendar.ratopati.com/ad",
            }
        )
        self.config = self._load_config()

    def _load_config(self) -> RatopatiConfig:
        response = self.session.get("https://calendar.ratopati.com/ad", timeout=30)
        response.raise_for_status()
        html = response.text

        api_match = re.search(r'api_base_url:"([^"]+)"', html)
        encrypt_match = re.search(r'aeed:"([^"]+)"', html)
        key_match = re.search(r'aek:"([^"]+)"', html)

        if not api_match or not encrypt_match or not key_match:
            raise RuntimeError("Could not recover Ratopati public config from page HTML.")

        api_base_url = api_match.group(1)
        encryption_enabled = encrypt_match.group(1).lower() == "true"
        key_material = base64.b64decode(key_match.group(1)).decode("utf-8")[3:-4]

        return RatopatiConfig(
            api_base_url=api_base_url,
            encryption_enabled=encryption_enabled,
            key=key_material,
        )

    def _decrypt_payload(self, payload: str) -> str:
        if not self.config.encryption_enabled:
            return payload

        proc = subprocess.run(
            [
                "openssl",
                "enc",
                "-aes-256-ecb",
                "-d",
                "-K",
                self.config.key.encode("utf-8").hex(),
                "-nosalt",
            ],
            input=base64.b64decode(payload),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return proc.stdout.decode("utf-8")

    def fetch_json(self, path: str) -> dict[str, Any] | list[Any]:
        response = self.session.get(f"{self.config.api_base_url}/{path}", timeout=30)
        response.raise_for_status()
        payload = response.json()
        encrypted = payload.get("data")
        if encrypted is None:
            raise RuntimeError(f"Unexpected payload shape for {path}: {payload}")
        return json.loads(self._decrypt_payload(encrypted))


def build_provider_inventory(
    start_year: int,
    end_year: int,
    coverage_path: Path,
    archive_path: Path,
) -> dict[str, Any]:
    return {
        "_meta": {
            "name": "Digital Calendar Providers",
            "last_updated": str(date.today()),
            "notes": (
                "Machine-readable calendar providers archived as secondary "
                "cross-validation pools. These are not official government "
                "holiday publications."
            ),
        },
        "providers": [
            {
                "provider_name": "ratopati_calendar",
                "homepage_url": "https://calendar.ratopati.com/ad",
                "api_base_url": "https://calapp.ratopati.com/api",
                "source_type": "secondary_digital_provider",
                "supported_bs_year_range": [1990, 2100],
                "supported_ad_year_range": [1944, 2039],
                "payload_encoding": "aes_256_ecb_with_public_client_key",
                "public_endpoints": [
                    "/calendar/{bs_year}/{bs_month}",
                    "/calendar/ad/{ad_year}/{ad_month}",
                    "/calendar/today-date",
                    "/calendar/upcoming-events",
                    "/calendar/holidays/{bs_year}/{bs_month}",
                    "/convert-date",
                ],
                "harvested_range_bs": [start_year, end_year],
                "artifacts": [
                    str(coverage_path.relative_to(ROOT)),
                    str(archive_path.relative_to(ROOT)),
                ],
                "notes": (
                    "Provider range was recovered from the public frontend year "
                    "option lists and verified against live decoded month responses."
                ),
            }
        ],
    }


def harvest_range(start_year: int, end_year: int) -> tuple[dict[str, Any], dict[str, Any]]:
    harvester = RatopatiHarvester()

    coverage_rows: list[dict[str, Any]] = []
    day_records: list[dict[str, Any]] = []

    for bs_year in range(start_year, end_year + 1):
        yearly_months = 0
        yearly_event_days = 0
        yearly_holiday_days = 0
        yearly_event_count = 0
        yearly_holiday_event_count = 0

        for bs_month in range(1, 13):
            month_payload = harvester.fetch_json(f"calendar/{bs_year}/{bs_month}")
            current_days = month_payload.get("current_month_days", [])

            event_days = 0
            holiday_days = 0
            event_count = 0
            holiday_event_count = 0

            for day in current_days:
                events = day.get("events") or []
                if not events:
                    continue

                event_days += 1
                holiday_flags = [bool(event.get("is_holiday")) for event in events]
                if any(holiday_flags):
                    holiday_days += 1

                normalized_events = []
                for event in events:
                    event_count += 1
                    is_holiday = bool(event.get("is_holiday"))
                    if is_holiday:
                        holiday_event_count += 1
                    normalized_events.append(
                        {
                            "title_np": event.get("title_np", ""),
                            "event_type": event.get("event_type", ""),
                            "is_holiday": is_holiday,
                            "time_from": event.get("time_from", ""),
                            "time_to": event.get("time_to", ""),
                        }
                    )

                day_records.append(
                    {
                        "source_name": "ratopati_calendar",
                        "source_type": "secondary_digital_provider",
                        "bs_year": bs_year,
                        "bs_month": bs_month,
                        "bs_day": int(day.get("bs_day_en", 0) or 0),
                        "bs_date_np": day.get("bs_date_np", ""),
                        "ad_date_en": day.get("ad_date_en", ""),
                        "day_en": day.get("day_en", ""),
                        "day_np": day.get("day_np", ""),
                        "tithi_title_np": (day.get("tithi") or {}).get("title_np", ""),
                        "pakshya_np": (day.get("panchanga") or {}).get("pakshya_np", ""),
                        "events": normalized_events,
                    }
                )

            current_month = month_payload.get("current_month", {})
            coverage_rows.append(
                {
                    "bs_year": bs_year,
                    "bs_month": bs_month,
                    "month_bs": current_month.get("month_bs", ""),
                    "ad_year_en": current_month.get("ad_year_en", ""),
                    "day_count": len(current_days),
                    "event_days": event_days,
                    "holiday_days": holiday_days,
                    "event_count": event_count,
                    "holiday_event_count": holiday_event_count,
                }
            )

            yearly_months += 1
            yearly_event_days += event_days
            yearly_holiday_days += holiday_days
            yearly_event_count += event_count
            yearly_holiday_event_count += holiday_event_count

        coverage_rows.append(
            {
                "bs_year": bs_year,
                "summary": {
                    "months_harvested": yearly_months,
                    "event_days": yearly_event_days,
                    "holiday_days": yearly_holiday_days,
                    "event_count": yearly_event_count,
                    "holiday_event_count": yearly_holiday_event_count,
                },
            }
        )

    month_rows = [row for row in coverage_rows if "summary" not in row]
    year_rows = [row for row in coverage_rows if "summary" in row]

    coverage_doc = {
        "_meta": {
            "name": "Ratopati Month Coverage",
            "last_updated": str(date.today()),
            "range_bs": [start_year, end_year],
            "months_harvested": len(month_rows),
            "years_harvested": len(year_rows),
            "notes": (
                "Decoded from Ratopati calendar month endpoints. This is a "
                "secondary digital-provider layer, not an official publication."
            ),
        },
        "years": year_rows,
        "months": month_rows,
    }

    archive_doc = {
        "_meta": {
            "name": "Ratopati Event Day Archive",
            "last_updated": str(date.today()),
            "range_bs": [start_year, end_year],
            "event_day_records": len(day_records),
            "notes": (
                "Only days containing one or more embedded events are archived. "
                "Each day keeps the original event list returned by Ratopati's "
                "decoded month payload."
            ),
        },
        "records": day_records,
    }

    return coverage_doc, archive_doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2000)
    parser.add_argument("--end-year", type=int, default=2100)
    args = parser.parse_args(argv)

    if args.start_year > args.end_year:
        raise SystemExit("--start-year must be <= --end-year")

    coverage_path = (
        SOURCE_INVENTORY_DIR
        / f"ratopati_month_coverage_{args.start_year}_{args.end_year}.json"
    )
    archive_path = (
        SOURCE_ARCHIVE_DIR
        / f"event_days_{args.start_year}_{args.end_year}.json"
    )

    coverage_doc, archive_doc = harvest_range(args.start_year, args.end_year)

    provider_inventory = build_provider_inventory(
        args.start_year,
        args.end_year,
        coverage_path=coverage_path,
        archive_path=archive_path,
    )

    PROVIDER_INVENTORY_PATH.write_text(
        json.dumps(provider_inventory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    coverage_path.write_text(
        json.dumps(coverage_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    archive_path.write_text(
        json.dumps(archive_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {PROVIDER_INVENTORY_PATH}")
    print(f"Wrote {coverage_path}")
    print(f"Wrote {archive_path}")
    print(
        "Summary:",
        {
            "range_bs": [args.start_year, args.end_year],
            "months_harvested": coverage_doc["_meta"]["months_harvested"],
            "event_day_records": archive_doc["_meta"]["event_day_records"],
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
