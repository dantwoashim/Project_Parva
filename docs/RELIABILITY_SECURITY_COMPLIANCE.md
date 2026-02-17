# Reliability Engineering Specification (M30)

## Service Level Objectives (SLOs)

| SLO | Target | Measurement |
|-----|--------|-------------|
| Availability | 99.5% monthly | Uptime / total time |
| API Response (P95) | < 500ms | Conversion + festival endpoints |
| API Response (P99) | < 2000ms | All endpoints including panchanga |
| Cache Hit Ratio | > 80% | Precomputed data served from cache |
| Accuracy | ≥ 99% | Official overlap ground truth match |
| Cold Start | < 3s | Time to first response after deploy |

## Alerting Rules

```yaml
alerts:
  - name: high_error_rate
    condition: error_rate > 5% over 5m
    action: page_maintainer
    
  - name: high_latency
    condition: p95_latency > 1000ms over 5m
    action: notify_slack
    
  - name: accuracy_drop
    condition: benchmark_score < 95%
    action: block_release
    
  - name: source_stale
    condition: ground_truth_age > 90d
    action: notify_maintainer
    
  - name: cache_miss_spike
    condition: cache_miss_rate > 50% over 10m
    action: trigger_precompute
```

## Incident Playbooks

### P1: API Down
1. Check Render dashboard for deploy failures
2. Check ephemeris data file availability
3. Roll back to last known good deploy
4. Verify with `/api/engine/health`

### P2: Incorrect Festival Dates
1. Check ground_truth_overrides.json for current year
2. Compare V2 calculator output vs MoHA gazette
3. If V2 is wrong: add override, tag as `hotfix`
4. Run evaluation harness, publish mismatch report

### P3: Source Data Stale
1. Check MoHA website for new gazette
2. Run OCR pipeline on new PDFs
3. Update ground_truth_overrides.json
4. Rerun benchmark, update transparency log

## Degraded Confidence Mode

When source data is unavailable or stale:
- Responses include `"confidence": "degraded"`
- All dates switch to `"method": "computed"` (no overrides)
- Alert fires to prompt data refresh

## Chaos Testing Scenarios

| Scenario | Expected Behavior |
|----------|-------------------|
| Ephemeris file missing | Fallback to Moshier (built-in) |
| Ground truth file corrupt | Skip overrides, compute all dates |
| Network timeout to external ref | Return cached/computed with degraded confidence |
| Database unavailable | Webhook system degrades; core API unaffected |
| High load (100 req/s) | Serve from precomputed cache; degrade gracefully |

---

# Security Hardening Specification (M31)

## Supply Chain Controls

- All dependencies pinned to exact versions in `requirements.txt`
- `pip-audit` runs in CI on every PR
- No runtime network calls to external services (all computation local)
- Ephemeris data bundled with deploy (no remote fetch)

## CI Security Checks

```yaml
security_pipeline:
  - step: dependency_audit
    tool: pip-audit
    block_on: critical_vulnerability
    
  - step: secret_scan
    tool: gitleaks
    block_on: any_secret_detected
    
  - step: static_analysis
    tool: bandit
    block_on: high_severity
    
  - step: container_scan
    tool: trivy
    block_on: critical_cve
```

## Secrets Hygiene

- No secrets in source code (verified by gitleaks)
- API keys stored in Render environment variables only
- Webhook URLs stored in local JSON (not committed)
- No PII collected or stored

## Input Validation

- All date inputs validated: year [1900, 2200], month [1, 12], day [1, 31]
- Festival IDs sanitized against allowlist
- Query parameters bounded (max days=365, max years=50)
- No SQL/NoSQL injection surface (no database)

## Pen-Test Checklist

- [ ] Rate limiting on all endpoints
- [ ] CORS restricted to known origins in production
- [ ] No debug endpoints exposed in production
- [ ] Error messages don't leak internal paths
- [ ] All responses include security headers (CSP, X-Frame-Options)

---

# Compliance & Policy Specification (M32)

## Disclaimer

> **Parva provides computed astronomical dates for informational purposes.**
> Festival dates may vary by tradition, region, and religious authority.
> Parva is not an official government calendar and should not be used as the sole authority for religious observance timing.
> Always consult local religious authorities and official government gazettes for ceremonial timing.

## Policy Model

### Observance Variation Policy
- Multiple traditions may observe the same festival on different dates
- Parva returns **all valid interpretations** with tradition labels
- No single interpretation is marked as "correct" — all carry equal standing unless government gazette exists

### Non-Advisory Usage
- Parva does **not** provide astrological advice
- Muhurta calculations are mathematical, not prescriptive
- Users should consult qualified jyotish for life decisions

### Jurisdiction Handling
- Nepal: MoHA gazette overrides take highest priority
- India: Indian government panchang used as secondary reference
- Diaspora: Local astronomical conditions (sunrise) used for tithi
- International: UTC-based computation with timezone parameter

## Data Retention
- No user data collected (stateless API)
- Webhook URLs stored locally, deletable on request
- Transparency log is append-only public record

## API Terms of Service
- Free for all use (personal, commercial, educational)
- Attribution appreciated but not required
- No SLA guarantee on free tier
- Rate limits may apply during peak festival periods
