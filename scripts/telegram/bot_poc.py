#!/usr/bin/env python3
"""Telegram bot proof-of-concept for Project Parva.

This script keeps integration simple for zero-budget deployment:
- It can run in demo mode locally without Telegram API calls.
- If TELEGRAM_BOT_TOKEN is provided, it polls Telegram updates.
- Supported commands:
  - /panchanga [YYYY-MM-DD]
  - /upcoming [days]

Note: This is a PoC utility for Week 31 (plan week 79), not production bot infra.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import date
from typing import Dict, Optional
from urllib import parse, request


DEFAULT_API_BASE = "http://localhost:8000/v2/api"


def _http_get_json(url: str) -> Dict:
    with request.urlopen(url, timeout=15) as resp:  # nosec B310
        return json.loads(resp.read().decode("utf-8"))


def _http_post_json(url: str, payload: Dict) -> Dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=15) as resp:  # nosec B310
        return json.loads(resp.read().decode("utf-8"))


def cmd_panchanga(api_base: str, target_date: Optional[str]) -> str:
    value = target_date or date.today().isoformat()
    url = f"{api_base}/calendar/panchanga?date={parse.quote(value)}"
    data = _http_get_json(url)
    tithi = data.get("tithi", {})
    bs = data.get("bs_date", {})
    return (
        f"Panchanga {value}\n"
        f"BS: {bs.get('year')}-{bs.get('month')}-{bs.get('day')} ({bs.get('month_name')})\n"
        f"Tithi: {tithi.get('display_number', tithi.get('tithi'))} {tithi.get('paksha')} ({tithi.get('name')})"
    )


def cmd_upcoming(api_base: str, days: int) -> str:
    url = f"{api_base}/festivals/upcoming?days={days}"
    data = _http_get_json(url)
    festivals = data.get("festivals", [])[:7]
    if not festivals:
        return "No upcoming festivals found in selected range."

    lines = [f"Upcoming festivals (next {days} days):"]
    for row in festivals:
        lines.append(f"- {row.get('name')} on {row.get('start_date')} ({row.get('days_until')} days)")
    return "\n".join(lines)


def process_command(text: str, api_base: str) -> str:
    parts = text.strip().split()
    if not parts:
        return "Send /panchanga or /upcoming"

    cmd = parts[0].lower()
    if cmd == "/start":
        return "Namaste! Try /panchanga or /upcoming 30"
    if cmd == "/panchanga":
        target = parts[1] if len(parts) > 1 else None
        return cmd_panchanga(api_base, target)
    if cmd == "/upcoming":
        try:
            days = int(parts[1]) if len(parts) > 1 else 7
        except ValueError:
            days = 7
        return cmd_upcoming(api_base, max(1, min(days, 90)))
    return "Unknown command. Use /panchanga [YYYY-MM-DD] or /upcoming [days]"


def send_message(bot_token: str, chat_id: int, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    _http_post_json(url, {"chat_id": chat_id, "text": text})


def run_polling(bot_token: str, api_base: str, interval: float = 2.0) -> None:
    offset = 0
    print("Starting Telegram polling loop...")
    while True:
        url = (
            f"https://api.telegram.org/bot{bot_token}/getUpdates?"
            f"timeout=20&offset={offset}"
        )
        payload = _http_get_json(url)
        for update in payload.get("result", []):
            offset = max(offset, int(update["update_id"]) + 1)
            message = update.get("message") or {}
            text = message.get("text", "")
            chat = message.get("chat") or {}
            chat_id = chat.get("id")
            if not text or not chat_id:
                continue
            reply = process_command(text, api_base)
            send_message(bot_token, int(chat_id), reply)
        time.sleep(interval)


def run_demo(api_base: str) -> None:
    print("[DEMO] /panchanga")
    print(process_command("/panchanga", api_base))
    print("\n[DEMO] /upcoming 14")
    print(process_command("/upcoming 14", api_base))


def main() -> None:
    parser = argparse.ArgumentParser(description="Project Parva Telegram PoC")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--demo", action="store_true", help="Run local demo without Telegram")
    args = parser.parse_args()

    if args.demo:
        run_demo(args.api_base)
        return

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN or run with --demo")

    run_polling(token, args.api_base)


if __name__ == "__main__":
    main()
