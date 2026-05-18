# Final Distribution Verification Matrix

Generated: 2026-05-16T10:41:38.903999+00:00
Commit: 701260c133c3fd2d38ba8bf1c0b9798e7da7e0b6
Python: Python 3.11.4
Node: v20.20.2
npm: 10.9.8

## Summary

- pass: 58

## Commands

### git status --short

- status: pass
- exit_code: 0
- cwd: .

```text
M frontend/src/data/benchmarkSummary.json
 M public-benchmark/results/benchmark-summary.json
 M reports/phase_08_performance_sre/latency_baseline.json
 M scripts/benchmark/generate_benchmark_badge.py
```

### py -3.11 --version

- status: pass
- exit_code: 0
- cwd: .

```text
Python 3.11.4
```

### node --version (Node 20)

- status: pass
- exit_code: 0
- cwd: .

```text
v20.20.2
```

### npm --version (npm 10)

- status: pass
- exit_code: 0
- cwd: .

```text
10.9.8
```

### py -3.11 scripts/verify_environment.py

- status: pass
- exit_code: 0
- cwd: .

```text
      "detail": "Node v20.20.2 (managed via npx node@20)"
    },
    "npm": {
      "ok": true,
      "detail": "11.10.0"
    },
    "frontend_lockfile": {
      "ok": true,
      "detail": "frontend\\package-lock.json"
    }
  }
}
```

### py -3.11 scripts/release/regenerate_public_release_hashes.py --check

- status: pass
- exit_code: 0
- cwd: .

```text
{
  "manifest_ok": true,
  "manifest_path": "data/public/releases/parva-bs-public-demo.manifest.json",
  "ok": true,
  "signature_ok": true,
  "signature_path": "data/public/releases/parva-bs-public-demo.signature.json"
}
```

### py -3.11 scripts/parva_trust_verify.py

- status: pass
- exit_code: 0
- cwd: .

```text
  "release_checks": 22,
  "signature_checks": 3,
  "transparency_log": {
    "events": [
      "calendar.release.published"
    ],
    "log_path": "data/public/transparency-log/parva-log.jsonl",
    "total_entries": 9,
    "valid": true
  }
}
trust verification passed
```

### py -3.11 scripts/check_docs_links.py

- status: pass
- exit_code: 0
- cwd: .

```text
Documentation links verified.
```

### py -3.11 scripts/check_path_leaks.py

- status: pass
- exit_code: 0
- cwd: .

```text
No local path leaks detected.
```

### py -3.11 scripts/check_future_bs_public_leakage.py

- status: pass
- exit_code: 0
- cwd: .

```text
    "public_profile_apps",
    "research_route_gates",
    "public_claim_text",
    "public_sdk_defaults"
  ]
}
{"event": "auth.denied", "path": "/v4/api/future-bs/month-lengths/2085", "method": "GET", "request_id": "01622f1fc5354583a146ee6eaccef4f3", "policy": "experimental_read", "principal": null, "reason": "credentials_missing", "client_ip": "testclient"}
{"event": "request.complete", "request_id": "01622f1fc5354583a146ee6eaccef4f3", "path": "/v4/api/future-bs/month-lengths/2085", "method": "GET", "status_code": 401, "latency_ms": 0.77, "principal": null, "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v4/api/future-bs/month-lengths/2085 "HTTP/1.1 401 Unauthorized"
{"event": "auth.denied", "path": "/v5/api/calendar-model-risk/prediction/2089/6", "method": "GET", "request_id": "12fe6efb2633482a90bad604b54c5eb5", "policy": "experimental_read", "principal": null, "reason": "credentials_missing", "client_ip": "testclient"}
{"event": "request.complete", "request_id": "12fe6efb2633482a90bad604b54c5eb5", "path": "/v5/api/calendar-model-risk/prediction/2089/6", "method": "GET", "status_code": 401, "latency_ms": 0.36, "principal": null, "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v5/api/calendar-model-risk/prediction/2089/6 "HTTP/1.1 401 Unauthorized"
```

### PYTHONPATH=backend:. py -3.11 scripts/release/check_public_openapi_drift.py

- status: pass
- exit_code: 0
- cwd: .

```text
Wrote C:\Users\prabi\AppData\Local\Temp\parva-openapi-iwiot5p2\openapi.json with 387 paths.
Static public OpenAPI mirror is current.
```

### py -3.11 scripts/release/check_public_claims.py

- status: pass
- exit_code: 0
- cwd: .

```text
Public claims check passed.
```

### py -3.11 scripts/release/verify_clean_clone_assumptions.py

- status: pass
- exit_code: 0
- cwd: .

```text
Clean-clone public verification assumptions passed.
```

### py -3.11 scripts/release/check_archive_hygiene.py

- status: pass
- exit_code: 0
- cwd: .

```text
{
  "ok": true,
  "required_paths": 9
}
```

### py -3.11 scripts/release/check_package_readiness.py

- status: pass
- exit_code: 0
- cwd: .

```text
{
  "ok": true,
  "python_packages": 3,
  "npm_packages": 1
}
```

### py -3.11 scripts/validate_external_temporal_rules.py

- status: pass
- exit_code: 0
- cwd: .

```text
External temporal rule registry passed.
```

### py -3.11 public-benchmark/validate_benchmark.py

- status: pass
- exit_code: 0
- cwd: .

```text
{
  "claim_boundary": "technical_benchmark_not_authority",
  "ok": true,
  "schema": "public-benchmark/schema.json",
  "tasks": 38
}
```

### py -3.11 public-benchmark/runners/run_against_static_baseline.py

- status: pass
- exit_code: 0
- cwd: .

```text
  ],
  "runner": "static_baseline",
  "schema_version": "2026-05-15.nepali-time-reliability.v0",
  "summary": {
    "max_score": 3800,
    "passed": 10,
    "score": 780,
    "score_percent": 20.53,
    "total": 38,
    "unsupported": 28
  }
}
```

### py -3.11 public-benchmark/runners/run_against_parva.py

- status: pass
- exit_code: 0
- cwd: .

```text
{"event": "auth.skipped", "path": "/v3/api/trust/sources", "method": "GET", "request_id": "31edd586f783401c99096d683bc3e767", "policy": "trust_read", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "31edd586f783401c99096d683bc3e767", "path": "/v3/api/trust/sources", "method": "GET", "status_code": 200, "latency_ms": 2.46, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/trust/sources "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/policy", "method": "GET", "request_id": "66c9b7bfa5ad4b54abd01116d2a6e327", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "66c9b7bfa5ad4b54abd01116d2a6e327", "path": "/v3/api/policy", "method": "GET", "status_code": 200, "latency_ms": 1.53, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/policy "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/trust/capabilities", "method": "GET", "request_id": "7ebd616c80f34758904b3fff95b4eed2", "policy": "trust_read", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "7ebd616c80f34758904b3fff95b4eed2", "path": "/v3/api/trust/capabilities", "method": "GET", "status_code": 200, "latency_ms": 1.4, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/trust/capabilities "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/trust/releases", "method": "GET", "request_id": "22f1e153daa04eefbb761ad0e07b0950", "policy": "trust_read", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "22f1e153daa04eefbb761ad0e07b0950", "path": "/v3/api/trust/releases", "method": "GET", "status_code": 200, "latency_ms": 2.01, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/trust/releases "HTTP/1.1 200 OK"
```

### py -3.11 public-benchmark/runners/compare_results.py

- status: pass
- exit_code: 0
- cwd: .

```text
  "score_gap_percent": 68.94,
  "static_score_percent": 20.53,
  "static_summary": {
    "max_score": 3800,
    "passed": 10,
    "score": 780,
    "score_percent": 20.53,
    "total": 38,
    "unsupported": 28
  },
  "unsupported_tasks": []
}
```

### py -3.11 scripts/benchmark/generate_benchmark_badge.py

- status: pass
- exit_code: 0
- cwd: .

```text
  "generated_at": "2026-05-16T00:11:15+05:45",
  "parva_score_percent": 89.47,
  "review_gate_performance": {
    "passed": 7,
    "score_percent": 100.0,
    "tasks": 7
  },
  "score_gap_percent": 68.94,
  "source": "public-benchmark/results/comparison.json",
  "static_score_percent": 20.53,
  "task_count": 38
}
```

### py -3.11 -m pytest -q -m not private/research lanes --maxfail=20

- status: pass
- exit_code: 0
- cwd: .

```text
.............................................................ss...s..s.s [ 17%]
........................................................................ [ 26%]
........................................................................ [ 34%]
........................................................................ [ 43%]
........................................................................ [ 52%]
..........................................................s............. [ 60%]
........................................................................ [ 69%]
........................................................................ [ 78%]
........................................................................ [ 86%]
........................................................................ [ 95%]
......................................                                   [100%]
824 passed, 6 skipped, 64 deselected in 117.08s (0:01:57)
```

### py -3.11 -m pytest tests/benchmark -q

- status: pass
- exit_code: 0
- cwd: .

```text
.......                                                                  [100%]
7 passed in 0.11s
```

### py -3.11 -m pytest tests/ephemeris -q

- status: pass
- exit_code: 0
- cwd: .

```text
........                                                                 [100%]
8 passed in 0.35s
```

### py -3.11 -m pytest tests/rules -q

- status: pass
- exit_code: 0
- cwd: .

```text
...                                                                      [100%]
3 passed in 0.07s
```

### py -3.11 -m pytest tests/release -q

- status: pass
- exit_code: 0
- cwd: .

```text
..........                                                               [100%]
10 passed in 3.01s
```

### py -3.11 scripts/perf/route_latency_smoke.py --profile public_reference --output reports/phase_08_performance_sre/latency_baseline.json

- status: pass
- exit_code: 0
- cwd: .

```text
{"event": "auth.skipped", "path": "/v3/api/protocol/version", "method": "GET", "request_id": "121c3bb48bca45c3b2fce5a14b7f074c", "policy": "protocol_read", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "121c3bb48bca45c3b2fce5a14b7f074c", "path": "/v3/api/protocol/version", "method": "GET", "status_code": 200, "latency_ms": 0.87, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/protocol/version "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/protocol/version", "method": "GET", "request_id": "895cf0874fbe4767b9a28d40e8f922ed", "policy": "protocol_read", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "895cf0874fbe4767b9a28d40e8f922ed", "path": "/v3/api/protocol/version", "method": "GET", "status_code": 200, "latency_ms": 1.27, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/protocol/version "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/protocol/version", "method": "GET", "request_id": "eb702750f4804bd79b2b8315397904e4", "policy": "protocol_read", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "eb702750f4804bd79b2b8315397904e4", "path": "/v3/api/protocol/version", "method": "GET", "status_code": 200, "latency_ms": 1.16, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/protocol/version "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/protocol/version", "method": "GET", "request_id": "68d2db03d1ac48ff85eff731e13edea9", "policy": "protocol_read", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "68d2db03d1ac48ff85eff731e13edea9", "path": "/v3/api/protocol/version", "method": "GET", "status_code": 200, "latency_ms": 1.0, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/protocol/version "HTTP/1.1 200 OK"
```

### py -3.11 scripts/check_canonical_runtime.py

- status: pass
- exit_code: 0
- cwd: .

```text
Canonical runtime registry check passed.
```

### py -3.11 scripts/check_maturity_lanes.py

- status: pass
- exit_code: 0
- cwd: .

```text
    "public_reference": {
      "allow_research_private": false,
      "route_count": 249
    },
    "research_private": {
      "allow_research_private": true,
      "route_count": 39
    }
  },
  "route_entry_count": 50,
  "subsystem_count": 31
}
```

### py -3.11 tools/validate_schemas.py

- status: pass
- exit_code: 0
- cwd: .

```text
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
validated 31 schemas
```

### py -3.11 scripts/release/check_route_inventory.py

- status: pass
- exit_code: 0
- cwd: .

```text
{
  "ok": true,
  "route_count": 448,
  "canonical_v3_route_count": 217,
  "legacy_route_count": 217
}
```

### py -3.11 scripts/release/check_documented_routes.py

- status: pass
- exit_code: 0
- cwd: .

```text
Documented route inventory verified (217 canonical v3 routes).
```

### py -3.11 scripts/release/check_backend_smoke.py

- status: pass
- exit_code: 0
- cwd: .

```text
{"event": "auth.skipped", "path": "/v3/api/calendar/convert", "method": "GET", "request_id": "3327320403d140129eb15bd0ec3cd910", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "3327320403d140129eb15bd0ec3cd910", "path": "/v3/api/calendar/convert", "method": "GET", "status_code": 200, "latency_ms": 12.09, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/calendar/convert?date=2026-10-21 "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/festivals/upcoming", "method": "GET", "request_id": "272271994be9438690decfa13b6b0e3f", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "272271994be9438690decfa13b6b0e3f", "path": "/v3/api/festivals/upcoming", "method": "GET", "status_code": 200, "latency_ms": 1262.82, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/festivals/upcoming?days=30 "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/policy", "method": "GET", "request_id": "f63092c4bc304e858a015dd0ee549597", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "f63092c4bc304e858a015dd0ee549597", "path": "/v3/api/policy", "method": "GET", "status_code": 200, "latency_ms": 1.71, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/policy "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/personal/panchanga", "method": "POST", "request_id": "3b74b7f6518b42e8838a29fa3ee9e4d7", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "3b74b7f6518b42e8838a29fa3ee9e4d7", "path": "/v3/api/personal/panchanga", "method": "POST", "status_code": 200, "latency_ms": 10.01, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: POST http://testserver/v3/api/personal/panchanga "HTTP/1.1 200 OK"
```

### py -3.11 scripts/parva_timegraph_verify.py

- status: pass
- exit_code: 0
- cwd: .

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

### py -3.11 scripts/parva_rulelang_verify.py

- status: pass
- exit_code: 0
- cwd: .

```text
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

### py -3.11 scripts/parva_impact_verify.py

- status: pass
- exit_code: 0
- cwd: .

```text
Project Parva impact verification
{
  "ok": true,
  "fixture_impacts": 2
}
impact verification passed
```

### py -3.11 scripts/parva_agent_verify.py

- status: pass
- exit_code: 0
- cwd: .

```text
Project Parva agent verification
{
  "ok": true,
  "tool_count": 14,
  "schedule_items": 2
}
agent verification passed
```

### py -3.11 scripts/parva_protocol_verify.py

- status: pass
- exit_code: 0
- cwd: .

```text
Project Parva protocol verification
{
  "ok": true,
  "conformance_tests": 20
}
protocol verification passed
```

### py -3.11 scripts/release/check_public_safety_gate.py

- status: pass
- exit_code: 0
- cwd: .

```text
PASS protocol schema validation
PASS public text safety
Public safety gate passed.
{"event": "auth.skipped", "path": "/openapi.json", "method": "GET", "request_id": "ba1324567fc24fa6977c148d63bebabb", "policy": "public", "principal": null, "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "ba1324567fc24fa6977c148d63bebabb", "path": "/openapi.json", "method": "GET", "status_code": 200, "latency_ms": 577.71, "principal": null, "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/openapi.json "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/openapi.json", "method": "GET", "request_id": "30d27f2499d84e6fb209d0c90ce2350d", "policy": "public", "principal": null, "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "30d27f2499d84e6fb209d0c90ce2350d", "path": "/openapi.json", "method": "GET", "status_code": 200, "latency_ms": 64.2, "principal": null, "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/openapi.json "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/calendar/bs-to-gregorian", "method": "POST", "request_id": "b05c2f7d207c4abdb069543381673725", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "b05c2f7d207c4abdb069543381673725", "path": "/v3/api/calendar/bs-to-gregorian", "method": "POST", "status_code": 403, "latency_ms": 2.5, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: POST http://testserver/v3/api/calendar/bs-to-gregorian "HTTP/1.1 403 Forbidden"
```

### py -3.11 scripts/release/check_render_blueprint.py

- status: pass
- exit_code: 0
- cwd: .

```text
Render blueprint check passed.
```

### py -3.11 scripts/release/check_repo_hygiene.py

- status: pass
- exit_code: 0
- cwd: .

```text
Repository hygiene check passed.
```

### py -3.11 scripts/frontend/check_component_size.py

- status: pass
- exit_code: 0
- cwd: .

```text
Frontend component size report: 1 production files exceed 700 lines.
 1002 frontend/src/pages/FeedSubscriptionsPage.jsx within-budget budget=1050
```

### py -3.11 -m ruff check backend tests scripts sdk packages/parva-python packages/parva-agent-tools packages/parva-mcp-server

- status: pass
- exit_code: 0
- cwd: .

```text
All checks passed!
```

### py -3.11 -m pytest packages/parva-python/tests -q

- status: pass
- exit_code: 0
- cwd: .

```text
..................                                                       [100%]
18 passed in 1.05s
```

### py -3.11 -m build packages/parva-python

- status: pass
- exit_code: 0
- cwd: .

```text
* Installing packages in isolated environment:
  - setuptools>=82.0.1
  - wheel>=0.45.0
* Getting build dependencies for sdist...
* Building sdist...
* Building wheel from sdist
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - setuptools>=82.0.1
  - wheel>=0.45.0
* Getting build dependencies for wheel...
* Building wheel...
```

### py -3.11 -m pytest packages/parva-agent-tools/tests -q

- status: pass
- exit_code: 0
- cwd: .

```text
........                                                                 [100%]
8 passed in 0.09s
```

### py -3.11 packages/parva-agent-tools/examples/basic_usage.py

- status: pass
- exit_code: 0
- cwd: .

```text
decision_support_not_authority
review_required=False
```

### py -3.11 -m pytest packages/parva-mcp-server/tests -q

- status: pass
- exit_code: 0
- cwd: .

```text
..........                                                               [100%]
10 passed in 0.05s
```

### py -3.11 -m parva_mcp_server.server --manifest

- status: pass
- exit_code: 0
- cwd: .

```text
      "route": "/v3/api/calendar/panchanga"
    },
    {
      "claim_boundary": "decision_support_not_authority",
      "method": "POST",
      "name": "check_temporal_claim",
      "read_only": true,
      "review_required_passthrough": true,
      "route": "/v3/api/agent/verify-claim"
    }
  ]
}
```

### py -3.11 -m parva_mcp_server.server --check

- status: pass
- exit_code: 0
- cwd: .

```text
  "ok": true,
  "probe": {
    "claim_boundary": "decision_support_not_authority",
    "method": "GET",
    "review_required": true,
    "route": "/v3/api/calendar/convert",
    "status": "manifest_only",
    "tool": "convert_ad_to_bs"
  },
  "resource_count": 6,
  "tool_count": 9
}
```

### py -3.11 scripts/release/check_mcp_registry_metadata.py

- status: pass
- exit_code: 0
- cwd: .

```text
{
  "ok": true,
  "metadata": "D:\\Project_Parva-main\\packages\\parva-mcp-server\\mcp-server.json"
}
```

### npm --prefix packages/parva-js test (Node 20/npm 10)

- status: pass
- exit_code: 0
- cwd: .

```text
  ---
  duration_ms: 0.7384
  ...
1..16
# tests 16
# suites 0
# pass 16
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 114.8422
```

### npm pack --dry-run in packages/parva-js (Node 20/npm 10)

- status: pass
- exit_code: 0
- cwd: packages\parva-js

```text
npm notice 26.4kB dist/index.js.map
npm notice 746B package.json
npm notice Tarball Details
npm notice name: @project-parva/parva-js
npm notice version: 0.3.0-alpha.0
npm notice filename: project-parva-parva-js-0.3.0-alpha.0.tgz
npm notice package size: 13.7 kB
npm notice unpacked size: 79.1 kB
npm notice shasum: 3888e90a2d4bc871415e1fdba56a28ca0dd87c1b
npm notice integrity: sha512-bDW31EuZzBcc5[...]O+QFBoc4w1uAQ==
npm notice total files: 5
npm notice
```

### npm --prefix frontend run lint (Node 20/npm 10)

- status: pass
- exit_code: 0
- cwd: .

```text
> frontend@3.0.0 lint
> eslint .
```

### npm --prefix frontend test -- --run (Node 20/npm 10)

- status: pass
- exit_code: 0
- cwd: .

```text
 [32mâœ“[39m src/test/memberContextState.test.js [2m([22m[2m8 tests[22m[2m)[22m[32m 28[2mms[22m[39m
 [32mâœ“[39m src/test/feedApi.test.js [2m([22m[2m1 test[22m[2m)[22m[32m 27[2mms[22m[39m
 [32mâœ“[39m src/test/CapabilityGating.test.jsx [2m([22m[2m5 tests[22m[2m)[22m[32m 24[2mms[22m[39m
 [32mâœ“[39m src/test/experimentalChronology.test.js [2m([22m[2m2 tests[22m[2m)[22m[32m 17[2mms[22m[39m
 [32mâœ“[39m src/test/errorFormatting.test.js [2m([22m[2m3 tests[22m[2m)[22m[32m 7[2mms[22m[39m
 [32mâœ“[39m src/test/apiBase.test.js [2m([22m[2m3 tests[22m[2m)[22m[32m 6[2mms[22m[39m
 [32mâœ“[39m src/test/i18nMessages.test.js [2m([22m[2m3 tests[22m[2m)[22m[32m 7[2mms[22m[39m

[2m Test Files [22m [1m[32m27 passed[39m[22m[90m (27)[39m
[2m      Tests [22m [1m[32m121 passed[39m[22m[90m (121)[39m
[2m   Start at [22m 16:22:33
[2m   Duration [22m 24.67s[2m (transform 4.32s, setup 16.08s, collect 19.47s, tests 44.85s, environment 60.73s, prepare 8.94s)[22m
```

### npm --prefix frontend run build (Node 20/npm 10)

- status: pass
- exit_code: 0
- cwd: .

```text
> vite build

[36mvite v7.3.3 [32mbuilding client environment for production...[36m[39m
transforming...
[32mâœ“[39m 87 modules transformed.
rendering chunks...
computing gzip size...
[2mdist/[22m[32mindex.html                 [39m[1m[2m  1.80 kB[22m[1m[22m[2m â”‚ gzip:  0.63 kB[22m
[2mdist/[22m[35massets/index-DlNJmNOP.css  [39m[1m[2m146.02 kB[22m[1m[22m[2m â”‚ gzip: 28.09 kB[22m
[2mdist/[22m[36massets/index-CrP1OSWj.js   [39m[1m[2m185.43 kB[22m[1m[22m[2m â”‚ gzip: 49.61 kB[22m
[2mdist/[22m[36massets/vendor-jDDfj8MR.js  [39m[1m[2m229.11 kB[22m[1m[22m[2m â”‚ gzip: 73.45 kB[22m
[32mâœ“ built in 2.46s[39m
```

### py -3.11 samples/digital-panchanga-release/2083-bs/verification/verify_release.py

- status: pass
- exit_code: 0
- cwd: .

```text
Sample digital Panchanga release verified.
```

### py -3.11 scripts/release/verify_public.py

- status: pass
- exit_code: 0
- cwd: .

```text
{"event": "auth.skipped", "path": "/v3/api/calendar/convert", "method": "GET", "request_id": "32934933eb654f33b127c75538c19397", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "32934933eb654f33b127c75538c19397", "path": "/v3/api/calendar/convert", "method": "GET", "status_code": 200, "latency_ms": 11.52, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/calendar/convert?date=2026-10-21 "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/festivals/upcoming", "method": "GET", "request_id": "a5c28ce9bb694a93b7ef7b84bb3908e6", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "a5c28ce9bb694a93b7ef7b84bb3908e6", "path": "/v3/api/festivals/upcoming", "method": "GET", "status_code": 200, "latency_ms": 1277.18, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/festivals/upcoming?days=30 "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/policy", "method": "GET", "request_id": "efbb069ce11341fd85df2aa6761e4e67", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "efbb069ce11341fd85df2aa6761e4e67", "path": "/v3/api/policy", "method": "GET", "status_code": 200, "latency_ms": 1.81, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: GET http://testserver/v3/api/policy "HTTP/1.1 200 OK"
{"event": "auth.skipped", "path": "/v3/api/personal/panchanga", "method": "POST", "request_id": "187cef3c718c41eaa203b7991dbf3e2f", "policy": "public", "principal": "testclient", "reason": null, "client_ip": "testclient"}
{"event": "request.complete", "request_id": "187cef3c718c41eaa203b7991dbf3e2f", "path": "/v3/api/personal/panchanga", "method": "POST", "status_code": 200, "latency_ms": 9.3, "principal": "testclient", "client_ip": "testclient", "version": "3.0.0"}
HTTP Request: POST http://testserver/v3/api/personal/panchanga "HTTP/1.1 200 OK"
```
