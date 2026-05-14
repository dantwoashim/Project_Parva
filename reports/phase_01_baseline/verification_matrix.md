# Phase 01 Verification Matrix



Generated at: `2026-05-14T00:50:33+00:00`



| Command run | Requested command | Status | Exit code | Category | Seconds | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| py -3.11 scripts/release/check_repo_hygiene.py | python scripts/release/check_repo_hygiene.py | pass | 0 |  | 0.189 | Repository hygiene check passed. |
| py -3.11 scripts/security/scan_repo_secrets.py | python scripts/security/scan_repo_secrets.py | pass | 0 |  | 7.127 | Secret scan passed. |
| py -3.11 scripts/check_path_leaks.py | python scripts/check_path_leaks.py | fail | 1 | private-data issue | 31.356 | parva_codex_phase_files\phase_06_trust_data_governance_and_source_authority.md:151: rg "data/source_archive\|data/future_bs/private\|/Users/\|C:\\\|private" data docs schemas specs backend frontend packages scripts tests \|\| true |
| py -3.11 scripts/check_docs_links.py | python scripts/check_docs_links.py | fail | 1 | repo issue | 0.167 | docs\strategy\PROJECT_PARVA_10_10_SOTA_MASTER_PLAN.md:817: missing path docs/internal_archive |
| py -3.11 tools/validate_schemas.py | python tools/validate_schemas.py | pass | 0 |  | 0.152 | validated 30 schemas |
| py -3.11 scripts/release/check_route_inventory.py | python scripts/release/check_route_inventory.py | pass | 0 |  | 2.482 | } |
| py -3.11 scripts/release/check_documented_routes.py | python scripts/release/check_documented_routes.py | pass | 0 |  | 2.069 | Documented route inventory verified (217 canonical v3 routes). |
| py -3.11 scripts/release/check_backend_smoke.py | python scripts/release/check_backend_smoke.py | pass | 0 |  | 5.079 | HTTP Request: POST http://testserver/v3/api/personal/panchanga "HTTP/1.1 200 OK" |
| py -3.11 scripts/release/verify_public.py | python scripts/release/verify_public.py | fail | 1 | private-data issue | 75.562 | [verify-public] FAIL: path leak scan exited 1 |
| py -3.11 scripts/parva_trust_verify.py | python scripts/parva_trust_verify.py | pass | 0 |  | 2.288 | trust verification passed |
| py -3.11 scripts/parva_timegraph_verify.py | python scripts/parva_timegraph_verify.py | pass | 0 |  | 3.009 | timegraph verification passed |
| py -3.11 scripts/parva_rulelang_verify.py | python scripts/parva_rulelang_verify.py | pass | 0 |  | 2.669 | rulelang verification passed |
| py -3.11 scripts/parva_impact_verify.py | python scripts/parva_impact_verify.py | pass | 0 |  | 2.684 | impact verification passed |
| py -3.11 scripts/parva_agent_verify.py | python scripts/parva_agent_verify.py | pass | 0 |  | 1.912 | agent verification passed |
| py -3.11 scripts/parva_agent_benchmark.py | python scripts/parva_agent_benchmark.py | pass | 0 |  | 1.84 | } |
| py -3.11 scripts/parva_protocol_verify.py | python scripts/parva_protocol_verify.py | pass | 0 |  | 1.111 | protocol verification passed |
| py -3.11 scripts/parva_conformance.py --target local --level parva_core | python scripts/parva_conformance.py --target local --level parva_core | pass | 0 |  | 1.077 | } |
| py -3.11 scripts/parva_offline_bundle.py --output dist/parva-offline-bundle | python scripts/parva_offline_bundle.py --output dist/parva-offline-bundle | pass | 0 |  | 1.286 | } |
| py -3.11 scripts/parva_offline_verify.py dist/parva-offline-bundle | python scripts/parva_offline_verify.py dist/parva-offline-bundle | pass | 0 |  | 0.705 | } |
| py -3.11 -m ruff check backend tests scripts sdk packages/parva-python | python -m ruff check backend tests scripts sdk packages/parva-python | pass | 0 |  | 0.461 | All checks passed! |
| py -3.11 -m pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=10 | pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=10 | pass | 0 |  | 145.245 | 780 passed, 8 skipped in 141.50s (0:02:21) |
| py -3.11 -m pytest packages/parva-python/tests -q | python -m pytest packages/parva-python/tests -q | pass | 0 |  | 1.572 | 14 passed in 0.92s |
| npm --prefix packages/parva-js test | npm --prefix packages/parva-js test | pass | 0 |  | 3.558 | â„¹ duration_ms 106.2592 |
| npm --prefix frontend run lint | npm --prefix frontend run lint | pass | 0 |  | 16.277 | > eslint . |
| npm --prefix frontend run build | npm --prefix frontend run build | pass | 0 |  | 3.265 | [32mâœ“ built in 2.21s[39m |
| npm --prefix frontend test -- --run | npm --prefix frontend test -- --run | pass | 0 |  | 29.332 | (Use `node --trace-warnings ...` to show where the warning was created) |



## Command Output Tails



### `py -3.11 scripts/release/check_repo_hygiene.py`

- requested_command: `python scripts/release/check_repo_hygiene.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `0.189`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
Repository hygiene check passed.
```

stderr tail:

```text

```

### `py -3.11 scripts/security/scan_repo_secrets.py`

- requested_command: `python scripts/security/scan_repo_secrets.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `7.127`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
Secret scan passed.
```

stderr tail:

```text

```

### `py -3.11 scripts/check_path_leaks.py`

- requested_command: `python scripts/check_path_leaks.py`
- status: `fail`
- exit_code: `1`
- duration_seconds: `31.356`
- failure_category: `private-data issue`
- blocking_reason: ``

stdout tail:

```text
repomix-project-parva-main.xml:197229: re.compile(r&quot;(?&lt;![A-Za-z0-9+.-])/Users/[^/\s]+/&quot;),
repomix-project-parva-main.xml:197230: re.compile(r&quot;(?&lt;![A-Za-z0-9+.-])/home/[^/\s]+/&quot;),
parva_codex_phase_files\phase_06_trust_data_governance_and_source_authority.md:151: rg "data/source_archive|data/future_bs/private|/Users/|C:\\|private" data docs schemas specs backend frontend packages scripts tests || true
```

stderr tail:

```text

```

### `py -3.11 scripts/check_docs_links.py`

- requested_command: `python scripts/check_docs_links.py`
- status: `fail`
- exit_code: `1`
- duration_seconds: `0.167`
- failure_category: `repo issue`
- blocking_reason: ``

stdout tail:

```text
docs\strategy\PROJECT_PARVA_10_10_SOTA_MASTER_PLAN.md:817: missing path docs/internal_archive
```

stderr tail:

```text

```

### `py -3.11 tools/validate_schemas.py`

- requested_command: `python tools/validate_schemas.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `0.152`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
ok: schemas\calendar-release.schema.json
ok: schemas\release-manifest.schema.json
ok: schemas\source-ref.schema.json
ok: schemas\source-registry.schema.json
ok: schemas\artifact-hash.schema.json
ok: schemas\signature.schema.json
ok: schemas\transparency-log-entry.schema.json
ok: schemas\temporal-sbom.schema.json
ok: schemas\calculation-trace.schema.json
ok: schemas\future-risk.schema.json
ok: schemas\blinded-audit-report.schema.json
ok: schemas\reconciliation-event.schema.json
ok: schemas\festival-occurrence.schema.json
ok: schemas\panchanga-day.schema.json
ok: schemas\nepal-fiscal-year.schema.json
ok: schemas\parva-protocol\agent-tool.schema.json
ok: schemas\parva-protocol\calendar-credential.schema.json
ok: schemas\parva-protocol\confidence.schema.json
ok: schemas\parva-protocol\conformance-report.schema.json
ok: schemas\parva-protocol\evidence-packet.schema.json
ok: schemas\parva-protocol\impact-report.schema.json
ok: schemas\parva-protocol\institutional-profile.schema.json
ok: schemas\parva-protocol\offline-bundle-manifest.schema.json
ok: schemas\parva-protocol\release-manifest.schema.json
ok: schemas\parva-protocol\rulelang-rule.schema.json
ok: schemas\parva-protocol\source-record.schema.json
ok: schemas\parva-protocol\timegraph-fact.schema.json
ok: schemas\parva-protocol\timegraph-relationship.schema.json
ok: schemas\parva-protocol\trust-log-entry.schema.json
validated 30 schemas
```

stderr tail:

```text

```

### `py -3.11 scripts/release/check_route_inventory.py`

- requested_command: `python scripts/release/check_route_inventory.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `2.482`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
{
  "ok": true,
  "route_count": 448,
  "canonical_v3_route_count": 217,
  "legacy_route_count": 217
}
```

stderr tail:

```text

```

### `py -3.11 scripts/release/check_documented_routes.py`

- requested_command: `python scripts/release/check_documented_routes.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `2.069`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
Documented route inventory verified (217 canonical v3 routes).
```

stderr tail:

```text

```

### `py -3.11 scripts/release/check_backend_smoke.py`

- requested_command: `python scripts/release/check_backend_smoke.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `5.079`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
Backend smoke checks passed.
```

stderr tail:

```text
{"event": "auth.skipped", "path": "/health", "method": "GET", "request_id": "bfe31e81e8a3495fb382cc3ef9e7f4db", "policy": "public", "principal": null, "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "bfe31e81e8a3495fb382cc3ef9e7f4db", "path": "/health", "method": "GET", "status_code": 200, "latency_ms": 3.92, "principal": null, "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/health "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/health/ready", "method": "GET", "request_id": "ea34fd3f10bc4a8f8689543c249901a7", "policy": "public", "principal": null, "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "ea34fd3f10bc4a8f8689543c249901a7", "path": "/health/ready", "method": "GET", "status_code": 200, "latency_ms": 3.47, "principal": null, "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/health/ready "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/calendar/today", "method": "GET", "request_id": "1dc87be92b4c4238857f5ec85d8fd7f2", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "1dc87be92b4c4238857f5ec85d8fd7f2", "path": "/v3/api/calendar/today", "method": "GET", "status_code": 200, "latency_ms": 10.39, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/calendar/today "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/calendar/convert", "method": "GET", "request_id": "24ba61790e2c425c804180e4384c2d02", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "24ba61790e2c425c804180e4384c2d02", "path": "/v3/api/calendar/convert", "method": "GET", "status_code": 200, "latency_ms": 16.7, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/calendar/convert?date=2026-10-21 "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/festivals/upcoming", "method": "GET", "request_id": "90d65823dd5946dbb68a536d73ce058f", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "90d65823dd5946dbb68a536d73ce058f", "path": "/v3/api/festivals/upcoming", "method": "GET", "status_code": 200, "latency_ms": 2331.77, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/festivals/upcoming?days=30 "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/policy", "method": "GET", "request_id": "74dd219d94db4e52bc9c4e18dcdb6969", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "74dd219d94db4e52bc9c4e18dcdb6969", "path": "/v3/api/policy", "method": "GET", "status_code": 200, "latency_ms": 4.55, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/policy "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/personal/panchanga", "method": "POST", "request_id": "ed6d0095a9b94a54866c3abb1debca09", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "ed6d0095a9b94a54866c3abb1debca09", "path": "/v3/api/personal/panchanga", "method": "POST", "status_code": 200, "latency_ms": 25.19, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: POST http://testserver/v3/api/personal/panchanga "HTTP/1.1 200 OK"
```

### `py -3.11 scripts/release/verify_public.py`

- requested_command: `python scripts/release/verify_public.py`
- status: `fail`
- exit_code: `1`
- duration_seconds: `75.562`
- failure_category: `private-data issue`
- blocking_reason: ``

stdout tail:

```text
      "ok": true,
      "detail": "11.10.0"
    },
    "frontend_lockfile": {
      "ok": true,
      "detail": "frontend\\package-lock.json"
    }
  }
}
Repository hygiene check passed.
Secret scan passed.
repomix-project-parva-main.xml:197229: re.compile(r&quot;(?&lt;![A-Za-z0-9+.-])/Users/[^/\s]+/&quot;),
repomix-project-parva-main.xml:197230: re.compile(r&quot;(?&lt;![A-Za-z0-9+.-])/home/[^/\s]+/&quot;),
parva_codex_phase_files\phase_06_trust_data_governance_and_source_authority.md:151: rg "data/source_archive|data/future_bs/private|/Users/|C:\\|private" data docs schemas specs backend frontend packages scripts tests || true

[verify-public] environment
[verify-public] C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/verify_environment.py
[verify-public] PASS: environment

[verify-public] repository hygiene
[verify-public] C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/release/check_repo_hygiene.py
[verify-public] PASS: repository hygiene

[verify-public] secret scan
[verify-public] C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/security/scan_repo_secrets.py
[verify-public] PASS: secret scan

[verify-public] path leak scan
[verify-public] C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe scripts/check_path_leaks.py
[verify-public] FAIL: path leak scan exited 1
```

stderr tail:

```text

```

### `py -3.11 scripts/parva_trust_verify.py`

- requested_command: `python scripts/parva_trust_verify.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `2.288`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
        "artifact_id": "conformance-report-schema",
        "expected_sha256": "a6127221f85519bc082a5a53489b8bbe128c42b9b40f38864a9228a3048df0b8",
        "ok": true,
        "path": "schemas/parva-protocol/conformance-report.schema.json"
      },
      {
        "actual_sha256": "d9f86fa12a65e0b41e5c3dd0325912ea7612b6a8a2c178ac10d7bf3ff92d0165",
        "artifact_id": "offline-bundle-manifest-schema",
        "expected_sha256": "d9f86fa12a65e0b41e5c3dd0325912ea7612b6a8a2c178ac10d7bf3ff92d0165",
        "ok": true,
        "path": "schemas/parva-protocol/offline-bundle-manifest.schema.json"
      }
    ],
    "issues": [],
    "ok": true,
    "source_count": 11,
    "trust_log_entries": 1
  },
  "release_checks": 22,
  "signature_checks": 3,
  "transparency_log": {
    "events": [
      "calendar.release.published"
    ],
    "log_path": "data/public/transparency-log/parva-log.jsonl",
    "total_entries": 8,
    "valid": true
  }
}
trust verification passed
```

stderr tail:

```text

```

### `py -3.11 scripts/parva_timegraph_verify.py`

- requested_command: `python scripts/parva_timegraph_verify.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `3.009`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
Project Parva TimeGraph verification
{
  "conflict_count": 1,
  "fact_count": 7416,
  "ok": true,
  "relationship_count": 27755,
  "release_id": "parva-bs-public-demo",
  "sample_date_query_items": 3,
  "sample_trace_sources": 1
}
timegraph verification passed
```

stderr tail:

```text

```

### `py -3.11 scripts/parva_rulelang_verify.py`

- requested_command: `python scripts/parva_rulelang_verify.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `2.669`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
            "WEEKDAY",
            "CONFIDENCE_POLICY_SATISFIED"
          ]
        }
      ],
      "rule_id": "payroll_previous_working_day_if_non_working",
      "rule_version": "1.0.0",
      "summary": {
        "failed": 0,
        "passed": 1,
        "total": 1
      }
    }
  ],
  "ok": true,
  "rule_count": 5,
  "sample_decision": {
    "reason_codes": [
      "RULE_VALIDATED",
      "INPUT_VALIDATED",
      "LAST_WORKING_DAY_SELECTED",
      "WEEKDAY",
      "NO_MATCHING_PUBLIC_HOLIDAY",
      "CONFIDENCE_POLICY_SATISFIED"
    ],
    "requires_human_review": false,
    "status": "approved"
  }
}
rulelang verification passed
```

stderr tail:

```text

```

### `py -3.11 scripts/parva_impact_verify.py`

- requested_command: `python scripts/parva_impact_verify.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `2.684`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
Project Parva impact verification
{
  "ok": true,
  "fixture_impacts": 2
}
impact verification passed
```

stderr tail:

```text

```

### `py -3.11 scripts/parva_agent_verify.py`

- requested_command: `python scripts/parva_agent_verify.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `1.912`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
Project Parva agent verification
{
  "ok": true,
  "tool_count": 14,
  "schedule_items": 2
}
agent verification passed
```

stderr tail:

```text

```

### `py -3.11 scripts/parva_agent_benchmark.py`

- requested_command: `python scripts/parva_agent_benchmark.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `1.84`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
    },
    {
      "case_id": "payroll_sensitive_review_required",
      "status": "pass"
    },
    {
      "case_id": "banking_sensitive_review_required",
      "status": "pass"
    },
    {
      "case_id": "ambiguous_intent_requires_confirmation",
      "status": "pass"
    },
    {
      "case_id": "fiscal_lookup_tool",
      "status": "pass"
    },
    {
      "case_id": "schedule_public",
      "status": "pass"
    },
    {
      "case_id": "impact_reasoning_tool",
      "status": "pass"
    }
  ],
  "passed": 10,
  "failed": 0,
  "status": "pass"
}
```

stderr tail:

```text

```

### `py -3.11 scripts/parva_protocol_verify.py`

- requested_command: `python scripts/parva_protocol_verify.py`
- status: `pass`
- exit_code: `0`
- duration_seconds: `1.111`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
Project Parva protocol verification
{
  "ok": true,
  "conformance_tests": 9
}
protocol verification passed
```

stderr tail:

```text

```

### `py -3.11 scripts/parva_conformance.py --target local --level parva_core`

- requested_command: `python scripts/parva_conformance.py --target local --level parva_core`
- status: `pass`
- exit_code: `0`
- duration_seconds: `1.077`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
    },
    {
      "test_id": "source.fixture_not_official",
      "status": "pass",
      "note": "Fixture/research sources cannot claim official authority."
    },
    {
      "test_id": "source.registry_readable",
      "status": "pass",
      "note": "Public source registry exists and is readable."
    },
    {
      "test_id": "source.registry_claim_boundaries",
      "status": "pass",
      "note": "Public source records include claim boundary metadata."
    }
  ],
  "warnings": [],
  "meta": {
    "release_id": "parva-bs-public-demo",
    "protocol_version": "parva-protocol-0.1.0",
    "claim_boundary": "parva_protocol_preview_not_legal_authority",
    "warnings": [
      "public_protocol_preview_not_legal_authority"
    ],
    "trace_id": "protocol_trace_74c18f6414344e5d",
    "data_mode": "public"
  },
  "report_hash": "sha256:fb0296c339dc63b6a4df5f9b89c2801fbb1c41fa9e2d21c6b525e5674486fee6"
}
```

stderr tail:

```text

```

### `py -3.11 scripts/parva_offline_bundle.py --output dist/parva-offline-bundle`

- requested_command: `python scripts/parva_offline_bundle.py --output dist/parva-offline-bundle`
- status: `pass`
- exit_code: `0`
- duration_seconds: `1.286`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
{
  "ok": true,
  "output": "dist\\parva-offline-bundle",
  "contents": 19
}
```

stderr tail:

```text

```

### `py -3.11 scripts/parva_offline_verify.py dist/parva-offline-bundle`

- requested_command: `python scripts/parva_offline_verify.py dist/parva-offline-bundle`
- status: `pass`
- exit_code: `0`
- duration_seconds: `0.705`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
{
  "ok": true,
  "issues": [],
  "checked": 19
}
```

stderr tail:

```text

```

### `py -3.11 -m ruff check backend tests scripts sdk packages/parva-python`

- requested_command: `python -m ruff check backend tests scripts sdk packages/parva-python`
- status: `pass`
- exit_code: `0`
- duration_seconds: `0.461`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
All checks passed!
```

stderr tail:

```text

```

### `py -3.11 -m pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=10`

- requested_command: `pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=10`
- status: `pass`
- exit_code: `0`
- duration_seconds: `145.245`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
........................................................................ [  9%]
........................................................................ [ 18%]
....ss...s..s.s......................................................... [ 27%]
........................................................................ [ 36%]
........................................................................ [ 45%]
........................................................................ [ 54%]
.......s................................................................ [ 63%]
........................................................................ [ 73%]
....................................ss.................................. [ 82%]
........................................................................ [ 91%]
....................................................................     [100%]
780 passed, 8 skipped in 141.50s (0:02:21)
```

stderr tail:

```text

```

### `py -3.11 -m pytest packages/parva-python/tests -q`

- requested_command: `python -m pytest packages/parva-python/tests -q`
- status: `pass`
- exit_code: `0`
- duration_seconds: `1.572`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
..............                                                           [100%]
14 passed in 0.92s
```

stderr tail:

```text

```

### `npm --prefix packages/parva-js test`

- requested_command: `npm --prefix packages/parva-js test`
- status: `pass`
- exit_code: `0`
- duration_seconds: `3.558`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text

> @project-parva/parva-js@0.1.0-alpha.0 test
> npm run build && node --test tests/client.test.mjs


> @project-parva/parva-js@0.1.0-alpha.0 build
> tsc -p tsconfig.json

âœ” uses the public v3 base for conversion calls (2.6349ms)
âœ” uses the public v4 capabilities endpoint for future-BS capabilities (0.2543ms)
âœ” validateBsDate converts public 400 responses into a validation result (0.5096ms)
âœ” retries 429 responses using Retry-After (1.8139ms)
âœ” can disable retries (1.0262ms)
âœ” covers public month, fiscal, business-day, and policy endpoints (1.0947ms)
âœ” covers compliance profile and decision support endpoints (1.0759ms)
âœ” covers temporal trust helper endpoints (2.0285ms)
âœ” covers TimeGraph helper endpoints (0.9981ms)
âœ” covers RuleLang helper endpoints (0.7584ms)
âœ” covers impact, agent, and protocol helper endpoints (1.465ms)
âœ” prefers structured public error messages (0.2129ms)
âœ” preserves source-aware metadata from public responses (0.2279ms)
â„¹ tests 13
â„¹ suites 0
â„¹ pass 13
â„¹ fail 0
â„¹ cancelled 0
â„¹ skipped 0
â„¹ todo 0
â„¹ duration_ms 106.2592
```

stderr tail:

```text

```

### `npm --prefix frontend run lint`

- requested_command: `npm --prefix frontend run lint`
- status: `pass`
- exit_code: `0`
- duration_seconds: `16.277`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text

> frontend@3.0.0 lint
> eslint .

```

stderr tail:

```text

```

### `npm --prefix frontend run build`

- requested_command: `npm --prefix frontend run build`
- status: `pass`
- exit_code: `0`
- duration_seconds: `3.265`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text

> frontend@3.0.0 build
> vite build

[36mvite v7.3.3 [32mbuilding client environment for production...[36m[39m
transforming...
[32mâœ“[39m 72 modules transformed.
rendering chunks...
computing gzip size...
[2mdist/[22m[32mindex.html                 [39m[1m[2m  1.80 kB[22m[1m[22m[2m â”‚ gzip:  0.63 kB[22m
[2mdist/[22m[35massets/index-3TwIfSYw.css  [39m[1m[2m145.85 kB[22m[1m[22m[2m â”‚ gzip: 28.06 kB[22m
[2mdist/[22m[36massets/index-Br8jwiKP.js   [39m[1m[2m173.22 kB[22m[1m[22m[2m â”‚ gzip: 47.07 kB[22m
[2mdist/[22m[36massets/vendor-jDDfj8MR.js  [39m[1m[2m229.11 kB[22m[1m[22m[2m â”‚ gzip: 73.45 kB[22m
[32mâœ“ built in 2.21s[39m
```

stderr tail:

```text

```

### `npm --prefix frontend test -- --run`

- requested_command: `npm --prefix frontend test -- --run`
- status: `pass`
- exit_code: `0`
- duration_seconds: `29.332`
- failure_category: ``
- blocking_reason: ``

stdout tail:

```text
   [33m[2mâœ“[22m[39m MemberProvider[2m > [22mrecords reminder and integration success events only after persistence succeeds [33m 929[2mms[22m[39m
 [32mâœ“[39m src/test/TruthLabPage.test.jsx [2m([22m[2m1 test[22m[2m)[22m[33m 582[2mms[22m[39m
   [33m[2mâœ“[22m[39m TruthLabPage[2m > [22mrenders the dispute atlas and proof capsule [33m 574[2mms[22m[39m
 [32mâœ“[39m src/test/consumerViewModels.test.js [2m([22m[2m6 tests[22m[2m)[22m[32m 102[2mms[22m[39m
 [32mâœ“[39m src/test/ApiService.test.jsx [2m([22m[2m24 tests[22m[2m)[22m[32m 158[2mms[22m[39m
 [32mâœ“[39m src/test/ConsumerInteractions.test.jsx [2m([22m[2m7 tests[22m[2m)[22m[33m 16527[2mms[22m[39m
   [33m[2mâœ“[22m[39m consumer route interactions[2m > [22mrenders the festivals surface as an API-backed expandable list [33m 4406[2mms[22m[39m
   [33m[2mâœ“[22m[39m consumer route interactions[2m > [22mopens, applies, and resets the festival filter sheet [33m 4670[2mms[22m[39m
   [33m[2mâœ“[22m[39m consumer route interactions[2m > [22mpersists a followed festival into the saved workspace [33m 2355[2mms[22m[39m
   [33m[2mâœ“[22m[39m consumer route interactions[2m > [22mshows the interactive best-time surface [33m 916[2mms[22m[39m
   [33m[2mâœ“[22m[39m consumer route interactions[2m > [22mopens and dismisses the search dialog [33m 2012[2mms[22m[39m
   [33m[2mâœ“[22m[39m consumer route interactions[2m > [22mkeeps the festival detail route available for deep links [33m 1438[2mms[22m[39m
   [33m[2mâœ“[22m[39m consumer route interactions[2m > [22mshows the profile and saved-items surface [33m 726[2mms[22m[39m
 [32mâœ“[39m src/test/temporalContextState.test.js [2m([22m[2m6 tests[22m[2m)[22m[32m 128[2mms[22m[39m
 [32mâœ“[39m src/test/productDateTime.test.js [2m([22m[2m5 tests[22m[2m)[22m[32m 103[2mms[22m[39m
 [32mâœ“[39m src/test/memberStore.test.js [2m([22m[2m5 tests[22m[2m)[22m[32m 58[2mms[22m[39m
 [32mâœ“[39m src/test/experimentalChronology.test.js [2m([22m[2m2 tests[22m[2m)[22m[32m 32[2mms[22m[39m
 [32mâœ“[39m src/test/memberContextState.test.js [2m([22m[2m8 tests[22m[2m)[22m[32m 31[2mms[22m[39m
 [32mâœ“[39m src/test/FestivalDetailRitualSchema.test.jsx [2m([22m[2m1 test[22m[2m)[22m[33m 1190[2mms[22m[39m
   [33m[2mâœ“[22m[39m FestivalDetail ritual schema adapter[2m > [22mrenders ritual timeline when backend provides daily_rituals array [33m 1182[2mms[22m[39m
 [32mâœ“[39m src/test/errorFormatting.test.js [2m([22m[2m3 tests[22m[2m)[22m[32m 14[2mms[22m[39m
 [32mâœ“[39m src/test/feedApi.test.js [2m([22m[2m1 test[22m[2m)[22m[32m 21[2mms[22m[39m
 [32mâœ“[39m src/test/apiBase.test.js [2m([22m[2m3 tests[22m[2m)[22m[32m 19[2mms[22m[39m
 [32mâœ“[39m src/test/i18nMessages.test.js [2m([22m[2m3 tests[22m[2m)[22m[32m 8[2mms[22m[39m

[2m Test Files [22m [1m[32m25 passed[39m[22m[90m (25)[39m
[2m      Tests [22m [1m[32m112 passed[39m[22m[90m (112)[39m
[2m   Start at [22m 06:40:47
[2m   Duration [22m 27.68s[2m (transform 3.15s, setup 19.29s, collect 21.76s, tests 55.62s, environment 65.34s, prepare 7.95s)[22m

```

stderr tail:

```text
(node:3716) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:4904) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:20444) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:26284) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:23464) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:3204) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:13620) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:16336) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:16604) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:27064) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:26972) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:3452) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:7764) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:16616) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
(node:19468) Warning: `--localstorage-file` was provided without a valid path
(Use `node --trace-warnings ...` to show where the warning was created)
```
