#!/usr/bin/env python3
"""Record public dateline acquisition status for AD/BS witness extraction."""

from __future__ import annotations

import json


def main() -> int:
    payload = {
        "rows": 0,
        "status": "blocked_no_bounded_seed_list",
        "source_family": "public_news_datelines",
        "reason": (
            "No vetted public dateline URL seed list is configured. Broad crawling was skipped to avoid "
            "over-crawling and source-policy ambiguity."
        ),
        "next_action": "Add public article URLs that visibly contain both AD and BS dates, then parse snippets.",
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
