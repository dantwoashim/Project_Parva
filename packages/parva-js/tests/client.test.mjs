import assert from "node:assert/strict";
import test from "node:test";
import {
  DEFAULT_API_BASE,
  DEFAULT_FUTURE_BS_CAPABILITIES_URL,
  ParvaClient,
} from "../dist/index.js";

function jsonResponse(payload, init = {}) {
  return {
    ok: init.ok ?? true,
    status: init.status ?? 200,
    statusText: init.statusText ?? "OK",
    text: async () => JSON.stringify(payload),
  };
}

test("uses the public v3 base for conversion calls", async () => {
  const calls = [];
  const client = new ParvaClient({
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      return jsonResponse({ gregorian: "2026-04-14" });
    },
  });

  const payload = await client.bsToAd({ year: 2083, month: 1, day: 1 });

  assert.equal(payload.gregorian, "2026-04-14");
  assert.equal(calls[0].url, `${DEFAULT_API_BASE}/calendar/bs-to-gregorian`);
  assert.equal(calls[0].init.method, "POST");
  assert.ok(calls[0].init.signal instanceof AbortSignal);
});

test("passes base URL overrides and timeout signals to fetch", async () => {
  const calls = [];
  const client = new ParvaClient({
    baseUrl: "https://calendar.example/v3/api/",
    timeoutMs: 50,
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      return jsonResponse({ english: "2026-04-14" });
    },
  });

  const payload = await client.adToBs("2026-04-14");

  assert.equal(payload.english, "2026-04-14");
  assert.equal(calls[0].url, "https://calendar.example/v3/api/calendar/convert?date=2026-04-14");
  assert.ok(calls[0].init.signal instanceof AbortSignal);
});

test("uses the public v4 capabilities endpoint for future-BS capabilities", async () => {
  const calls = [];
  const client = new ParvaClient({
    fetchImpl: async (url) => {
      calls.push(url);
      return jsonResponse({
        surface: "future_bs_risk_research",
        publication_status: "computed_prediction_not_official",
      });
    },
  });

  const payload = await client.getFutureBsCapabilities();

  assert.equal(payload.publication_status, "computed_prediction_not_official");
  assert.equal(calls[0], DEFAULT_FUTURE_BS_CAPABILITIES_URL);
});

test("validateBsDate converts public 400 responses into a validation result", async () => {
  let calls = 0;
  const client = new ParvaClient({
    fetchImpl: async () => {
      calls += 1;
      return jsonResponse({ detail: "Invalid BS date" }, {
        ok: false,
        status: 400,
        statusText: "Bad Request",
      });
    },
  });

  const result = await client.validateBsDate({ year: 2083, month: 1, day: 32 });

  assert.equal(result.valid, false);
  assert.equal(result.publication_status, "computed_prediction_not_official");
  assert.match(result.error, /Invalid BS date/);
  assert.equal(calls, 1);
});

test("request timeout is surfaced as a structured SDK error", async () => {
  const client = new ParvaClient({
    timeoutMs: 1,
    maxRetries: 0,
    fetchImpl: async (_url, init) => new Promise((_resolve, reject) => {
      init.signal.addEventListener("abort", () => {
        const error = new Error("aborted");
        error.name = "AbortError";
        reject(error);
      }, { once: true });
    }),
  });

  await assert.rejects(
    () => client.getToday(),
    /timed out after 1ms/,
  );
});

test("client does not expose private or exact research route helpers", () => {
  const methodNames = Object.getOwnPropertyNames(ParvaClient.prototype);
  const forbiddenFragments = [
    "admin",
    "auditPrivate",
    "backtest",
    "billing",
    "loanImpact",
    "monthLengthPrediction",
    "privateSource",
    "researchBacktest",
  ];
  const exposed = methodNames.filter((name) => (
    forbiddenFragments.some((fragment) => name.includes(fragment))
  ));

  assert.deepEqual(exposed, []);
});

test("retries 429 responses using Retry-After", async () => {
  const calls = [];
  const sleeps = [];
  const client = new ParvaClient({
    sleep: async (ms) => {
      sleeps.push(ms);
    },
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      if (calls.length === 1) {
        return {
          ok: false,
          status: 429,
          statusText: "Too Many Requests",
          headers: { get: (name) => (name === "Retry-After" ? "0.25" : null) },
          text: async () => JSON.stringify({ detail: "slow down" }),
        };
      }
      return jsonResponse({ gregorian: "2026-04-14" });
    },
  });

  const payload = await client.bsToAd({ year: 2083, month: 1, day: 1 });

  assert.equal(payload.gregorian, "2026-04-14");
  assert.equal(calls.length, 2);
  assert.deepEqual(sleeps, [250]);
});

test("can disable retries", async () => {
  let calls = 0;
  const client = new ParvaClient({
    maxRetries: 0,
    fetchImpl: async () => {
      calls += 1;
      return jsonResponse({ detail: "slow down" }, {
        ok: false,
        status: 429,
        statusText: "Too Many Requests",
      });
    },
  });

  await assert.rejects(
    () => client.bsToAd({ year: 2083, month: 1, day: 1 }),
    /status 429/,
  );
  assert.equal(calls, 1);
});

test("covers public month, fiscal, business-day, and policy endpoints", async () => {
  const calls = [];
  const client = new ParvaClient({
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      return jsonResponse({ ok: true });
    },
  });

  await client.getMonthCalendar(2026, 4);
  await client.getFiscalYear(2082);
  await client.getBsMonths(2082);
  await client.getBusinessDays({
    start_bs: "2082-01-01",
    end_bs: "2082-01-07",
  });
  await client.getEnterpriseCapabilities();
  await client.getPolicy();

  assert.equal(calls[0].url, `${DEFAULT_API_BASE}/calendar/dual-month?year=2026&month=4`);
  assert.equal(calls[1].url, `${DEFAULT_API_BASE}/enterprise/fiscal-year/2082`);
  assert.equal(calls[2].url, `${DEFAULT_API_BASE}/enterprise/bs-months/2082`);
  assert.equal(calls[3].url, `${DEFAULT_API_BASE}/enterprise/business-days`);
  assert.equal(calls[3].init.method, "POST");
  assert.equal(calls[4].url, `${DEFAULT_API_BASE}/enterprise/capabilities`);
  assert.equal(calls[5].url, `${DEFAULT_API_BASE}/policy`);
});

test("covers compliance profile and decision support endpoints", async () => {
  const calls = [];
  const meta = {
    source: {
      id: "parva_enterprise_compliance_profiles",
      label: "Parva enterprise compliance profile definitions",
      tier: "publisher_reference",
      authority: "derived_reference_not_legal_authority",
    },
    confidence: "source_backed",
    data_version: "parva-public-calendar-v1",
    claim_boundary: "enterprise_decision_support_not_legal_authority",
    warnings: ["not_legal_tax_or_banking_contract_authority"],
    trace_id: "trace",
  };
  const client = new ParvaClient({
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      return jsonResponse({ ok: true, meta });
    },
  });

  await client.listProfiles();
  await client.getProfile("nepal_private_company_default");
  const evaluated = await client.evaluateDate({
    profile_id: "nepal_private_company_default",
    bs_date: "2082-04-02",
  });
  await client.nextWorkingDay({ profile_id: "nepal_private_company_default", bs_date: "2082-04-04" });
  await client.previousWorkingDay({ profile_id: "nepal_private_company_default", bs_date: "2082-04-04" });
  await client.addWorkingDays({
    profile_id: "nepal_private_company_default",
    bs_date: "2082-04-02",
    working_days: 2,
  });
  await client.monthClosingDay({
    profile_id: "nepal_private_company_default",
    bs_year: 2082,
    bs_month: 4,
  });
  await client.fiscalPeriod({
    profile_id: "nepal_private_company_default",
    bs_date: "2082-04-02",
  });

  assert.equal(calls[0].url, `${DEFAULT_API_BASE}/compliance/profiles`);
  assert.equal(calls[1].url, `${DEFAULT_API_BASE}/compliance/profiles/nepal_private_company_default`);
  assert.equal(calls[2].url, `${DEFAULT_API_BASE}/compliance/evaluate-date`);
  assert.equal(calls[2].init.method, "POST");
  assert.deepEqual(JSON.parse(calls[2].init.body), {
    profile_id: "nepal_private_company_default",
    bs_date: "2082-04-02",
  });
  assert.equal(calls[3].url, `${DEFAULT_API_BASE}/compliance/next-working-day`);
  assert.equal(calls[4].url, `${DEFAULT_API_BASE}/compliance/previous-working-day`);
  assert.equal(calls[5].url, `${DEFAULT_API_BASE}/compliance/add-working-days`);
  assert.equal(calls[6].url, `${DEFAULT_API_BASE}/compliance/month-closing-day`);
  assert.equal(calls[7].url, `${DEFAULT_API_BASE}/compliance/fiscal-period`);
  assert.deepEqual(evaluated.meta, meta);
});

test("covers temporal trust helper endpoints", async () => {
  const calls = [];
  const packet = {
    packet_type: "date_conversion",
    release: { release_id: "parva-bs-public-demo" },
    integrity: {
      packet_hash: "sha256:abc",
      signature_status: "unsigned_public_preview",
    },
  };
  const client = new ParvaClient({
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      return jsonResponse(url.includes("/evidence/") ? packet : { ok: true });
    },
  });

  await client.getTrustCapabilities();
  await client.listSources({ release_id: "parva-bs-public-demo" });
  await client.getSource("parva_public_bs_ad_corpus");
  await client.listReleases();
  await client.getRelease("parva-bs-public-demo");
  await client.diffReleases("parva-bs-public-demo", "parva-bs-public-demo");
  await client.getTrustLog();
  const evidence = await client.createDateConversionEvidence({ ad_date: "2026-04-14" });
  await client.createComplianceDecisionEvidence({
    profile_id: "nepal_private_company_default",
    bs_date: "2082-04-02",
  });

  assert.equal(calls[0].url, `${DEFAULT_API_BASE}/trust/capabilities`);
  assert.equal(
    calls[1].url,
    `${DEFAULT_API_BASE}/trust/sources?release_id=parva-bs-public-demo`,
  );
  assert.equal(calls[2].url, `${DEFAULT_API_BASE}/trust/sources/parva_public_bs_ad_corpus`);
  assert.equal(calls[3].url, `${DEFAULT_API_BASE}/trust/releases`);
  assert.equal(calls[4].url, `${DEFAULT_API_BASE}/trust/releases/parva-bs-public-demo`);
  assert.equal(
    calls[5].url,
    `${DEFAULT_API_BASE}/trust/releases/parva-bs-public-demo/diff/parva-bs-public-demo`,
  );
  assert.equal(calls[6].url, `${DEFAULT_API_BASE}/trust/log`);
  assert.equal(calls[7].url, `${DEFAULT_API_BASE}/trust/evidence/date-conversion`);
  assert.equal(calls[7].init.method, "POST");
  assert.deepEqual(JSON.parse(calls[7].init.body), { ad_date: "2026-04-14" });
  assert.equal(calls[8].url, `${DEFAULT_API_BASE}/trust/evidence/compliance-decision`);
  assert.equal(evidence.integrity.packet_hash, "sha256:abc");
});

test("covers TimeGraph helper endpoints", async () => {
  const calls = [];
  const client = new ParvaClient({
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      return jsonResponse({
        items: [],
        fact: { fact_id: "fact_bs_ad_2083_01_01" },
        trace: { fact: { fact_id: "fact_bs_ad_2083_01_01" } },
        meta: { claim_boundary: "timegraph_query_not_legal_authority" },
      });
    },
  });

  await client.getTimeGraphCapabilities();
  await client.listFacts({ fact_type: "bs_ad_mapping", limit: 5, has_conflicts: false });
  await client.getFact("fact_bs_ad_2083_01_01");
  await client.queryFacts({ calendar: "BS", date: "2083-01-01" });
  await client.getFactsForDate("BS", "2083-01-01", { limit: 3 });
  await client.getFactsForSource("parva_public_bs_ad_corpus");
  await client.getFactsForRelease("parva-bs-public-demo", { limit: 2 });
  await client.getFactsForProfile("nepal_private_company_default");
  await client.getRelationships("fact_bs_ad_2083_01_01");
  await client.traceFact("fact_bs_ad_2083_01_01", { depth: 2 });
  await client.listConflicts();

  assert.equal(calls[0].url, `${DEFAULT_API_BASE}/timegraph/capabilities`);
  assert.equal(
    calls[1].url,
    `${DEFAULT_API_BASE}/timegraph/facts?fact_type=bs_ad_mapping&limit=5&has_conflicts=false`,
  );
  assert.equal(calls[2].url, `${DEFAULT_API_BASE}/timegraph/facts/fact_bs_ad_2083_01_01`);
  assert.equal(calls[3].url, `${DEFAULT_API_BASE}/timegraph/query`);
  assert.equal(calls[3].init.method, "POST");
  assert.deepEqual(JSON.parse(calls[3].init.body), { calendar: "BS", date: "2083-01-01" });
  assert.equal(calls[4].url, `${DEFAULT_API_BASE}/timegraph/date/BS/2083-01-01?limit=3`);
  assert.equal(
    calls[5].url,
    `${DEFAULT_API_BASE}/timegraph/sources/parva_public_bs_ad_corpus/facts`,
  );
  assert.equal(
    calls[6].url,
    `${DEFAULT_API_BASE}/timegraph/releases/parva-bs-public-demo/facts?limit=2`,
  );
  assert.equal(
    calls[7].url,
    `${DEFAULT_API_BASE}/timegraph/profiles/nepal_private_company_default/facts`,
  );
  assert.equal(
    calls[8].url,
    `${DEFAULT_API_BASE}/timegraph/entities/fact_bs_ad_2083_01_01/relationships`,
  );
  assert.equal(
    calls[9].url,
    `${DEFAULT_API_BASE}/timegraph/facts/fact_bs_ad_2083_01_01/trace?depth=2`,
  );
  assert.equal(calls[10].url, `${DEFAULT_API_BASE}/timegraph/conflicts`);
});

test("covers RuleLang helper endpoints", async () => {
  const calls = [];
  const client = new ParvaClient({
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      return jsonResponse({
        rule_id: "last_working_day_of_nepali_month",
        decision: { status: "approved", reason_codes: ["RULE_VALIDATED"] },
        trace: { steps: [] },
      });
    },
  });

  await client.getRuleCapabilities();
  await client.listRules();
  await client.getRule("last_working_day_of_nepali_month");
  await client.validateRule({ rule_id: "demo_rule" });
  await client.evaluateRule("last_working_day_of_nepali_month", {
    input: { bs_month: "2082-04" },
  });
  await client.testRule("last_working_day_of_nepali_month");
  await client.evaluateCustomRule({
    rule: { rule_id: "demo_rule" },
    input: { bs_date: "2082-04-02" },
  });
  await client.explainRule({
    rule_id: "last_working_day_of_nepali_month",
    input: { bs_month: "2082-04" },
  });

  assert.equal(calls[0].url, `${DEFAULT_API_BASE}/rules/capabilities`);
  assert.equal(calls[1].url, `${DEFAULT_API_BASE}/rules`);
  assert.equal(calls[2].url, `${DEFAULT_API_BASE}/rules/last_working_day_of_nepali_month`);
  assert.equal(calls[3].url, `${DEFAULT_API_BASE}/rules/validate`);
  assert.equal(calls[3].init.method, "POST");
  assert.deepEqual(JSON.parse(calls[3].init.body), { rule: { rule_id: "demo_rule" } });
  assert.equal(
    calls[4].url,
    `${DEFAULT_API_BASE}/rules/last_working_day_of_nepali_month/evaluate`,
  );
  assert.deepEqual(JSON.parse(calls[4].init.body), {
    input: { bs_month: "2082-04" },
    include_evidence: false,
  });
  assert.equal(calls[5].url, `${DEFAULT_API_BASE}/rules/last_working_day_of_nepali_month/test`);
  assert.equal(calls[6].url, `${DEFAULT_API_BASE}/rules/evaluate`);
  assert.equal(calls[7].url, `${DEFAULT_API_BASE}/rules/explain`);
});

test("covers impact, agent, and protocol helper endpoints", async () => {
  const calls = [];
  const client = new ParvaClient({
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      return jsonResponse({ ok: true });
    },
  });

  await client.getImpactCapabilities();
  await client.diffReleasesForImpact();
  await client.simulateChangeSet({ changes: [] });
  await client.simulateReleaseDiff();
  await client.getImpactRun("impact_run_demo");
  await client.listImpactReasonCodes();
  await client.listImpactRecommendedActions();
  await client.getImpactEventSchema();
  await client.getAgentCapabilities();
  await client.listAgentTools();
  await client.getAgentManifest();
  await client.resolveTemporalIntent("2083-01-01 BS maps to 2026-04-14 AD.");
  await client.verifyTemporalClaim({ claim: "2083-01-01 BS maps to 2026-04-14 AD." });
  await client.planSchedule({ schedule_type: "payroll", bs_year: 2082, months: [4] });
  await client.explainTemporalDecision({ type: "claim", claim: "demo" });
  await client.checkHumanReview({ requires_human_review: true });
  await client.draftRule("move payroll to next working day");
  await client.runAgentTool({ tool_name: "parva.get_capabilities", input: {} });
  await client.getProtocolVersion();
  await client.getProtocolCapabilities();
  await client.listProtocolSpecs();
  await client.listProtocolSchemas();
  await client.listCompatibilityLevels();
  await client.runConformance();
  await client.issueCalendarCredential({
    subject: { type: "date_conversion" },
    claims: { bs_date: "2083-01-01", ad_date: "2026-04-14" },
  });
  await client.verifyCalendarCredential({ credential_id: "demo" });
  await client.getOfflineBundleManifest();

  assert.equal(calls[0].url, `${DEFAULT_API_BASE}/impact/capabilities`);
  assert.equal(calls[1].url, `${DEFAULT_API_BASE}/impact/diff-releases`);
  assert.deepEqual(JSON.parse(calls[1].init.body), {
    from_release_id: "parva-bs-public-demo",
    to_release_id: "parva-bs-public-demo",
    include_fixture: false,
  });
  assert.equal(calls[2].url, `${DEFAULT_API_BASE}/impact/simulate-change-set`);
  assert.deepEqual(JSON.parse(calls[2].init.body), { change_set: { changes: [] } });
  assert.equal(calls[3].url, `${DEFAULT_API_BASE}/impact/simulate-release-diff`);
  assert.equal(calls[8].url, `${DEFAULT_API_BASE}/agent/capabilities`);
  assert.equal(calls[11].url, `${DEFAULT_API_BASE}/agent/resolve-intent`);
  assert.equal(calls[17].url, `${DEFAULT_API_BASE}/agent/run-tool`);
  assert.equal(calls[18].url, `${DEFAULT_API_BASE}/protocol/version`);
  assert.equal(calls[23].url, `${DEFAULT_API_BASE}/protocol/conformance/run`);
  assert.equal(calls[24].url, `${DEFAULT_API_BASE}/protocol/credentials/issue`);
  assert.equal(calls[25].url, `${DEFAULT_API_BASE}/protocol/credentials/verify`);
  assert.equal(calls[26].url, `${DEFAULT_API_BASE}/protocol/offline-bundle/manifest`);
});

test("prefers structured public error messages", async () => {
  const client = new ParvaClient({
    fetchImpl: async () => jsonResponse({
      error: {
        code: "BAD_REQUEST",
        message: "Use YYYY-MM-DD",
        details: {},
        trace_id: "test",
      },
    }, {
      ok: false,
      status: 400,
      statusText: "Bad Request",
    }),
  });

  const result = await client.validateBsDate({ year: 2083, month: 1, day: 32 });

  assert.equal(result.valid, false);
  assert.match(result.error, /Use YYYY-MM-DD/);
});

test("preserves source-aware metadata from public responses", async () => {
  const meta = {
    source: {
      id: "parva_public_bs_ad_corpus",
      label: "Parva public BS/AD corpus",
      tier: "software_table_reference",
      authority: "derived_reference_not_legal_authority",
      version: "parva-public-calendar-v1",
    },
    confidence: "source_backed",
    data_version: "parva-public-calendar-v1",
    claim_boundary: "public_corpus_reference_only",
    warnings: ["not_legal_tax_or_banking_contract_authority"],
    trace_id: "trace",
    result_class: "ad_to_bs_conversion",
  };
  const client = new ParvaClient({
    fetchImpl: async () => jsonResponse({ gregorian: "2026-04-14", meta }),
  });

  const payload = await client.adToBs("2026-04-14");

  assert.deepEqual(payload.meta, meta);
});

test("core SDK methods expose proof modes", async () => {
  const calls = [];
  const client = new ParvaClient({
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      return jsonResponse({ proof: { mode: "membrane" } });
    },
  });

  await client.adToBs("2025-04-14", { proof: "membrane" });
  await client.bsToAd({ year: 2082, month: 1, day: 1, proof: "membrane" });
  await client.validateBsDate({ year: 2082, month: 1, day: 1, proof: "membrane" });
  await client.checkHoliday({ bs_date: "2082-01-01", proof: "membrane" });
  await client.evaluateDate({ bs_date: "2082-01-01", proof: "membrane" });
  await client.getFiscalYear(2082, { proof: "membrane" });
  await client.getBsMonths(2082, { mode: "compare", proof: "membrane" });

  assert.equal(calls[0].url, `${DEFAULT_API_BASE}/calendar/convert?date=2025-04-14&proof=membrane`);
  assert.equal(calls[1].url, `${DEFAULT_API_BASE}/calendar/bs-to-gregorian?proof=membrane`);
  assert.deepEqual(JSON.parse(calls[1].init.body), { year: 2082, month: 1, day: 1 });
  assert.equal(calls[2].url, `${DEFAULT_API_BASE}/calendar/validate-bs-date?year=2082&month=1&day=1&proof=membrane`);
  assert.equal(
    calls[3].url,
    `${DEFAULT_API_BASE}/compliance/holiday?bs_date=2082-01-01&profile_id=nepal_public_general&proof=membrane`,
  );
  assert.equal(calls[4].url, `${DEFAULT_API_BASE}/compliance/evaluate-date?proof=membrane`);
  assert.equal(calls[5].url, `${DEFAULT_API_BASE}/enterprise/fiscal-year/2082?proof=membrane`);
  assert.equal(calls[6].url, `${DEFAULT_API_BASE}/enterprise/bs-months/2082?mode=compare&proof=membrane`);
});

test("SDK membrane verifier is structural and does not upgrade authority", () => {
  const client = new ParvaClient({ fetchImpl: async () => jsonResponse({}) });
  assert.equal(client.verifyMembrane({ kind: "parva_membrane" }).verified, false);
  assert.deepEqual(client.verifyMembrane({
    kind: "parva_membrane",
    canonical_query: { operation: "ad_to_bs" },
    identity_hash: "parva:id:v1:sha256:abc",
    result: { bs_date: "2082-01-01" },
    boundary: { claim_boundary: "decision_support_not_authority" },
    field_provenance: { bs_date: { authority: "static_reference" } },
    witness_hash: "parva:wit:v1:sha256:def",
  }), {
    verified: true,
    reason: "structural_checks_passed_replay_required_for_full_verification",
  });
});
