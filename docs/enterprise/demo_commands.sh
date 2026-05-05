#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

pretty() {
  "$PYTHON_BIN" -m json.tool
}

echo
echo "1. AD to BS conversion"
curl -s "$BASE_URL/v3/api/calendar/convert?date=2026-04-14" | pretty

echo
echo "2. BS to AD conversion"
curl -s -X POST "$BASE_URL/v3/api/calendar/bs-to-gregorian" \
  -H "Content-Type: application/json" \
  -d '{"year":2083,"month":1,"day":1}' | pretty

echo
echo "3. Conversion comparison"
curl -s "$BASE_URL/v3/api/calendar/convert/compare?date=2026-04-14" | pretty

echo
echo "4. Fiscal year"
curl -s "$BASE_URL/v3/api/enterprise/fiscal-year/2082" | pretty

echo
echo "5. BS month lengths"
curl -s "$BASE_URL/v3/api/enterprise/bs-months/2082" | pretty

echo
echo "6. Business days"
curl -s -X POST "$BASE_URL/v3/api/enterprise/business-days" \
  -H "Content-Type: application/json" \
  -d '{"start_bs":"2082-04-01","end_bs":"2082-04-31","weekend":"saturday","include_start":true,"include_end":true,"holiday_policy":"none"}' | pretty

echo
echo "7. Bulk conversion"
curl -s -X POST "$BASE_URL/v3/api/enterprise/bulk-convert" \
  -H "Content-Type: application/json" \
  -d '{"mode":"ad_to_bs","dates":["2026-04-14","2026-07-16","2025-07-17"]}' | pretty

echo
echo "8. Validation"
curl -s -X POST "$BASE_URL/v3/api/enterprise/validate" \
  -H "Content-Type: application/json" \
  -d '{"cases":[{"id":"ny-2083","type":"ad_to_bs","input":"2026-04-14","expected":"2083-01-01"},{"id":"fy-start-2082","type":"bs_to_ad","input":"2082-04-01","expected":"2025-07-17"}]}' | pretty
