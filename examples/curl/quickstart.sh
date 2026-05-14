#!/usr/bin/env sh
set -eu

BASE_URL="${PARVA_API_BASE:-https://api.prabinghimire1.com.np/v3/api}"

curl "$BASE_URL/calendar/today"
curl "$BASE_URL/calendar/convert?date=2026-04-14"
curl -X POST "$BASE_URL/calendar/bs-to-gregorian" \
  -H "Content-Type: application/json" \
  -d '{"year":2083,"month":1,"day":1}'
curl "$BASE_URL/trust/capabilities"
curl "$BASE_URL/protocol/version"
