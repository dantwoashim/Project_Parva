import {
  buildFutureBsUrl,
  buildUrl,
  extractErrorDetail,
  optionalParams,
  parseJsonSafely,
  trimTrailingSlash,
} from "./internal.js";

export const DEFAULT_API_BASE = "https://api.prabinghimire1.com.np/v3/api";
export const DEFAULT_FUTURE_BS_CAPABILITIES_URL =
  "https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities";

export type JsonObject = Record<string, unknown>;
export type ProofMode = "compact" | "audit" | "replay" | "membrane";

export interface SourceClaim {
  id: string;
  label: string;
  tier: string;
  authority: string;
  version?: string;
  url?: string;
  retrieved_at?: string;
}

export interface SourceAwareMeta {
  source: SourceClaim;
  confidence: string;
  data_version: string;
  claim_boundary: string;
  warnings: string[];
  trace_id?: string | null;
  result_class?: string;
}

export interface BsDateInput {
  year: number;
  month: number;
  day: number;
}

export interface ParvaClientOptions {
  baseUrl?: string;
  futureBsCapabilitiesUrl?: string;
  timeoutMs?: number;
  fetchImpl?: typeof fetch;
  maxRetries?: number;
  retryBaseDelayMs?: number;
  sleep?: (ms: number) => Promise<void>;
}

export interface ValidateBsDateResult {
  valid: boolean;
  publication_status: "computed_prediction_not_official";
  result?: JsonObject;
  error?: string;
}

export interface BusinessDaysInput {
  start_bs: string;
  end_bs: string;
  weekend?: "saturday" | "sunday" | "friday_saturday";
  include_start?: boolean;
  include_end?: boolean;
  holiday_policy?: "none" | "known_public_holidays";
}

export interface ComplianceDateInput {
  profile_id?: string;
  bs_date?: string;
  ad_date?: string;
  decision_intent?: string;
  proof?: ProofMode;
}

export interface HolidayInput {
  bs_date?: string;
  ad_date?: string;
  profile_id?: string;
  proof?: ProofMode;
}

export interface PanchangaInput {
  date: string;
  proof?: ProofMode;
  lat?: number;
  lon?: number;
  tz?: string;
  ephemeris_provider?: string;
  ephemeris_fixture_id?: string;
  ayanamsa?: string;
}

export interface WorkingDaySearchInput {
  profile_id?: string;
  bs_date?: string;
  ad_date?: string;
  include_input?: boolean;
}

export interface AddWorkingDaysInput {
  profile_id?: string;
  bs_date?: string;
  ad_date?: string;
  working_days: number;
}

export interface MonthClosingDayInput {
  profile_id?: string;
  bs_year: number;
  bs_month: number;
}

export interface TrustReleaseInput {
  release_id?: string;
}

export interface DateConversionEvidenceInput extends TrustReleaseInput {
  ad_date?: string;
  bs_date?: string;
}

export interface ComplianceEvidenceInput extends TrustReleaseInput {
  profile_id?: string;
  bs_date?: string;
  ad_date?: string;
  decision_intent?: string;
}

export interface TimeGraphQueryInput extends TrustReleaseInput {
  fact_type?: string;
  date?: string;
  calendar?: string;
  source_id?: string;
  profile_id?: string;
  confidence?: string;
  claim_boundary?: string;
  jurisdiction?: string;
  has_conflicts?: boolean;
  limit?: number;
  offset?: number;
}

export interface TimeGraphListInput extends TrustReleaseInput {
  limit?: number;
  offset?: number;
}

export interface RuleEvaluateInput extends TrustReleaseInput {
  input?: JsonObject;
  include_evidence?: boolean;
}

export interface CustomRuleEvaluateInput extends RuleEvaluateInput {
  rule: JsonObject;
}

export interface RuleExplainInput extends TrustReleaseInput {
  rule_id?: string;
  rule?: JsonObject;
  input?: JsonObject;
}

export interface ImpactReleaseDiffInput {
  from_release_id?: string;
  to_release_id?: string;
  include_fixture?: boolean;
  limit?: number;
}

export interface ImpactChangeSetInput {
  change_set?: JsonObject;
  changes?: JsonObject[];
  limit?: number;
  [key: string]: unknown;
}

export interface AgentClaimInput {
  claim: string;
  context?: JsonObject;
  include_evidence?: boolean;
}

export interface AgentScheduleInput {
  schedule_type?: string;
  bs_year: number;
  profile_id?: string;
  months?: number[];
  include_evidence?: boolean;
}

export interface AgentRunToolInput {
  tool_name: string;
  input?: JsonObject;
}

export interface ProtocolConformanceInput {
  target?: string;
  level?: string;
}

export interface ProtocolCredentialIssueInput {
  claim_type?: string;
  bs_date: string;
  release_id?: string;
  evidence_packet_id?: string;
}

export class ParvaApiError extends Error {
  readonly status?: number;
  readonly body?: unknown;
  readonly retryAfterMs?: number;

  constructor(message: string, status?: number, body?: unknown, retryAfterMs?: number) {
    super(message);
    this.name = "ParvaApiError";
    this.status = status;
    this.body = body;
    this.retryAfterMs = retryAfterMs;
  }
}

export class ParvaClient {
  readonly baseUrl: string;
  readonly futureBsCapabilitiesUrl: string;
  readonly timeoutMs: number;
  readonly maxRetries: number;
  readonly retryBaseDelayMs: number;
  private readonly fetchImpl: typeof fetch;
  private readonly sleep: (ms: number) => Promise<void>;

  constructor(options: ParvaClientOptions = {}) {
    this.baseUrl = trimTrailingSlash(options.baseUrl ?? DEFAULT_API_BASE);
    this.futureBsCapabilitiesUrl =
      options.futureBsCapabilitiesUrl ?? DEFAULT_FUTURE_BS_CAPABILITIES_URL;
    this.timeoutMs = options.timeoutMs ?? 10_000;
    this.maxRetries = Math.max(0, options.maxRetries ?? 2);
    this.retryBaseDelayMs = Math.max(0, options.retryBaseDelayMs ?? 250);
    this.fetchImpl = options.fetchImpl ?? globalThis.fetch;
    this.sleep = options.sleep ?? sleepMs;
    if (!this.fetchImpl) {
      throw new ParvaApiError("No fetch implementation is available for ParvaClient");
    }
  }

  async getToday(options: { riskMode?: string } = {}): Promise<JsonObject> {
    const params = options.riskMode ? { risk_mode: options.riskMode } : undefined;
    return this.request("GET", "/calendar/today", { params });
  }

  async adToBs(date: string, options: { proof?: ProofMode } = {}): Promise<JsonObject> {
    return this.request("GET", "/calendar/convert", {
      params: optionalParams({ date, proof: options.proof }),
    });
  }

  async bsToAd(input: BsDateInput & { proof?: ProofMode }): Promise<JsonObject> {
    const { proof, ...body } = input;
    return this.request("POST", "/calendar/bs-to-gregorian", {
      params: optionalParams({ proof }),
      json: body,
    });
  }

  async validateBsDate(input: BsDateInput & { proof?: ProofMode }): Promise<ValidateBsDateResult | JsonObject> {
    if (input.proof) {
      return this.request("GET", "/calendar/validate-bs-date", {
        params: optionalParams({
          year: input.year,
          month: input.month,
          day: input.day,
          proof: input.proof,
        }),
      });
    }
    try {
      const result = await this.bsToAd(input);
      return {
        valid: true,
        publication_status: "computed_prediction_not_official",
        result,
      };
    } catch (error) {
      if (error instanceof ParvaApiError && error.status === 400) {
        return {
          valid: false,
          publication_status: "computed_prediction_not_official",
          error: error.message,
        };
      }
      throw error;
    }
  }

  async getMonthCalendar(year: number, month: number): Promise<JsonObject> {
    return this.request("GET", "/calendar/dual-month", {
      params: { year: String(year), month: String(month) },
    });
  }

  async getFiscalYear(bsYear: number, options: { proof?: ProofMode } = {}): Promise<JsonObject> {
    return this.request("GET", `/enterprise/fiscal-year/${bsYear}`, {
      params: optionalParams({ proof: options.proof }),
    });
  }

  async getBsMonths(
    bsYear: number,
    options: { mode?: "canonical" | "solar_civil" | "static_lookup" | "compare"; proof?: ProofMode } = {},
  ): Promise<JsonObject> {
    return this.request("GET", `/enterprise/bs-months/${bsYear}`, {
      params: optionalParams({
        mode: options.mode && options.mode !== "canonical" ? options.mode : undefined,
        proof: options.proof,
      }),
    });
  }

  async getBusinessDays(input: BusinessDaysInput): Promise<JsonObject> {
    return this.request("POST", "/enterprise/business-days", { json: input });
  }

  async getEnterpriseCapabilities(): Promise<JsonObject> {
    return this.request("GET", "/enterprise/capabilities");
  }

  async listProfiles(): Promise<JsonObject> {
    return this.request("GET", "/compliance/profiles");
  }

  async getProfile(profileId: string): Promise<JsonObject> {
    return this.request("GET", `/compliance/profiles/${encodeURIComponent(profileId)}`);
  }

  async evaluateDate(input: ComplianceDateInput): Promise<JsonObject> {
    const { proof, ...body } = input;
    return this.request("POST", "/compliance/evaluate-date", {
      params: optionalParams({ proof }),
      json: body,
    });
  }

  async checkHoliday(input: HolidayInput): Promise<JsonObject> {
    return this.request("GET", "/compliance/holiday", {
      params: optionalParams({
        bs_date: input.bs_date,
        ad_date: input.ad_date,
        profile_id: input.profile_id ?? "nepal_public_general",
        proof: input.proof,
      }),
    });
  }

  async getPanchanga(input: PanchangaInput): Promise<JsonObject> {
    return this.request("GET", "/calendar/panchanga", {
      params: optionalParams({
        date: input.date,
        proof: input.proof,
        lat: input.lat,
        lon: input.lon,
        tz: input.tz ?? "Asia/Kathmandu",
        ephemeris_provider: input.ephemeris_provider ?? "builtin_swiss_moshier",
        ephemeris_fixture_id: input.ephemeris_fixture_id,
        ayanamsa: input.ayanamsa ?? "lahiri",
      }),
    });
  }

  verifyMembrane(membrane: JsonObject): { verified: boolean; reason: string; missing?: string[] } {
    const required = ["kind", "canonical_query", "identity_hash", "result", "boundary", "field_provenance", "witness_hash"];
    const missing = required.filter((key) => !(key in membrane));
    if (missing.length) {
      return { verified: false, reason: "required_fields_missing", missing };
    }
    if (typeof membrane.identity_hash !== "string" || !membrane.identity_hash.startsWith("parva:id:v1:sha256:")) {
      return { verified: false, reason: "identity_hash_invalid" };
    }
    if (typeof membrane.witness_hash !== "string" || !membrane.witness_hash.startsWith("parva:wit:v1:sha256:")) {
      return { verified: false, reason: "witness_hash_invalid" };
    }
    return { verified: true, reason: "structural_checks_passed_replay_required_for_full_verification" };
  }

  verifyProofPack(proofPack: JsonObject): { verified: boolean; reason: string; missing?: string[] } {
    if (proofPack.membrane && typeof proofPack.membrane === "object" && !Array.isArray(proofPack.membrane)) {
      return this.verifyMembrane(proofPack.membrane as JsonObject);
    }
    const required = ["identity_hash", "witness_hash", "boundary"];
    const missing = required.filter((key) => !(key in proofPack));
    return {
      verified: missing.length === 0,
      reason: missing.length === 0 ? "verified_compact_proofpack" : "required_fields_missing",
      missing,
    };
  }

  verifyTimepack(timepack: JsonObject): { verified: boolean; reason: string; missing?: string[] } {
    if (timepack.kind !== "parva_timepack" || !Array.isArray(timepack.proof_packs)) {
      return { verified: false, reason: "timepack_schema_invalid" };
    }
    for (const pack of timepack.proof_packs) {
      const result = this.verifyProofPack(pack as JsonObject);
      if (!result.verified) {
        return { verified: false, reason: `child_${result.reason}` };
      }
    }
    const boundary = timepack.boundary_summary as JsonObject | undefined;
    if (!boundary?.not_authority) {
      return { verified: false, reason: "timepack_boundary_summary_missing" };
    }
    return { verified: true, reason: "structural_checks_passed_replay_required_for_full_verification" };
  }

  replayPanchangaMembrane(membrane: JsonObject): { verified: boolean; reason: string; missing?: string[] } {
    const structural = this.verifyMembrane(membrane);
    if (!structural.verified) {
      return structural;
    }
    const query = membrane.canonical_query as JsonObject | undefined;
    if (query?.operation !== "panchanga_summary") {
      return { verified: false, reason: "not_panchanga_membrane" };
    }
    const metadata = membrane.ephemeris_metadata as JsonObject | undefined;
    if (!metadata?.provider_id || !metadata.provider_kind) {
      return { verified: false, reason: "ephemeris_metadata_missing" };
    }
    return { verified: true, reason: "structural_panchanga_checks_passed_local_kernel_or_backend_replay_required" };
  }

  async nextWorkingDay(input: WorkingDaySearchInput): Promise<JsonObject> {
    return this.request("POST", "/compliance/next-working-day", { json: input });
  }

  async previousWorkingDay(input: WorkingDaySearchInput): Promise<JsonObject> {
    return this.request("POST", "/compliance/previous-working-day", { json: input });
  }

  async addWorkingDays(input: AddWorkingDaysInput): Promise<JsonObject> {
    return this.request("POST", "/compliance/add-working-days", { json: input });
  }

  async monthClosingDay(input: MonthClosingDayInput): Promise<JsonObject> {
    return this.request("POST", "/compliance/month-closing-day", { json: input });
  }

  async fiscalPeriod(input: ComplianceDateInput): Promise<JsonObject> {
    return this.request("POST", "/compliance/fiscal-period", { json: input });
  }

  async getPolicy(): Promise<JsonObject> {
    return this.request("GET", "/policy");
  }

  async getTrustCapabilities(): Promise<JsonObject> {
    return this.request("GET", "/trust/capabilities");
  }

  async listSources(input: TrustReleaseInput = {}): Promise<JsonObject> {
    return this.request("GET", "/trust/sources", {
      params: optionalParams({ release_id: input.release_id }),
    });
  }

  async getSource(sourceId: string, input: TrustReleaseInput = {}): Promise<JsonObject> {
    return this.request("GET", `/trust/sources/${encodeURIComponent(sourceId)}`, {
      params: optionalParams({ release_id: input.release_id }),
    });
  }

  async listReleases(): Promise<JsonObject> {
    return this.request("GET", "/trust/releases");
  }

  async getRelease(releaseId: string): Promise<JsonObject> {
    return this.request("GET", `/trust/releases/${encodeURIComponent(releaseId)}`);
  }

  async diffReleases(fromRelease: string, toRelease: string): Promise<JsonObject> {
    return this.request(
      "GET",
      `/trust/releases/${encodeURIComponent(fromRelease)}/diff/${encodeURIComponent(toRelease)}`,
    );
  }

  async getTrustLog(input: TrustReleaseInput = {}): Promise<JsonObject> {
    return this.request("GET", "/trust/log", {
      params: optionalParams({ release_id: input.release_id }),
    });
  }

  async createDateConversionEvidence(input: DateConversionEvidenceInput): Promise<JsonObject> {
    return this.request("POST", "/trust/evidence/date-conversion", { json: input });
  }

  async createComplianceDecisionEvidence(input: ComplianceEvidenceInput): Promise<JsonObject> {
    return this.request("POST", "/trust/evidence/compliance-decision", { json: input });
  }

  async getTimeGraphCapabilities(): Promise<JsonObject> {
    return this.request("GET", "/timegraph/capabilities");
  }

  async getRuleCapabilities(): Promise<JsonObject> {
    return this.request("GET", "/rules/capabilities");
  }

  async listRules(): Promise<JsonObject> {
    return this.request("GET", "/rules");
  }

  async getRule(ruleId: string): Promise<JsonObject> {
    return this.request("GET", `/rules/${encodeURIComponent(ruleId)}`);
  }

  async validateRule(rule: JsonObject): Promise<JsonObject> {
    return this.request("POST", "/rules/validate", { json: { rule } });
  }

  async evaluateRule(ruleId: string, input: RuleEvaluateInput = {}): Promise<JsonObject> {
    return this.request("POST", `/rules/${encodeURIComponent(ruleId)}/evaluate`, {
      json: {
        input: input.input ?? {},
        release_id: input.release_id,
        include_evidence: input.include_evidence ?? false,
      },
    });
  }

  async testRule(ruleId: string): Promise<JsonObject> {
    return this.request("POST", `/rules/${encodeURIComponent(ruleId)}/test`, { json: {} });
  }

  async evaluateCustomRule(input: CustomRuleEvaluateInput): Promise<JsonObject> {
    return this.request("POST", "/rules/evaluate", {
      json: {
        rule: input.rule,
        input: input.input ?? {},
        release_id: input.release_id,
        include_evidence: input.include_evidence ?? false,
      },
    });
  }

  async explainRule(input: RuleExplainInput): Promise<JsonObject> {
    return this.request("POST", "/rules/explain", {
      json: {
        rule_id: input.rule_id,
        rule: input.rule,
        input: input.input ?? {},
        release_id: input.release_id,
      },
    });
  }

  async listFacts(input: TimeGraphQueryInput = {}): Promise<JsonObject> {
    return this.request("GET", "/timegraph/facts", { params: optionalParams(input) });
  }

  async getFact(factId: string, input: TrustReleaseInput = {}): Promise<JsonObject> {
    return this.request("GET", `/timegraph/facts/${encodeURIComponent(factId)}`, {
      params: optionalParams({ release_id: input.release_id }),
    });
  }

  async queryFacts(input: TimeGraphQueryInput): Promise<JsonObject> {
    return this.request("POST", "/timegraph/query", { json: input });
  }

  async getFactsForDate(
    calendar: string,
    date: string,
    input: TimeGraphListInput = {},
  ): Promise<JsonObject> {
    return this.request(
      "GET",
      `/timegraph/date/${encodeURIComponent(calendar)}/${encodeURIComponent(date)}`,
      { params: optionalParams(input) },
    );
  }

  async getFactsForSource(sourceId: string, input: TimeGraphListInput = {}): Promise<JsonObject> {
    return this.request("GET", `/timegraph/sources/${encodeURIComponent(sourceId)}/facts`, {
      params: optionalParams(input),
    });
  }

  async getFactsForRelease(releaseId: string, input: TimeGraphListInput = {}): Promise<JsonObject> {
    return this.request("GET", `/timegraph/releases/${encodeURIComponent(releaseId)}/facts`, {
      params: optionalParams(input),
    });
  }

  async getFactsForProfile(profileId: string, input: TimeGraphListInput = {}): Promise<JsonObject> {
    return this.request("GET", `/timegraph/profiles/${encodeURIComponent(profileId)}/facts`, {
      params: optionalParams(input),
    });
  }

  async getRelationships(entityId: string, input: TimeGraphListInput = {}): Promise<JsonObject> {
    return this.request(
      "GET",
      `/timegraph/entities/${encodeURIComponent(entityId)}/relationships`,
      { params: optionalParams(input) },
    );
  }

  async traceFact(
    factId: string,
    input: TrustReleaseInput & { depth?: number } = {},
  ): Promise<JsonObject> {
    return this.request("GET", `/timegraph/facts/${encodeURIComponent(factId)}/trace`, {
      params: optionalParams(input),
    });
  }

  async listConflicts(input: TimeGraphListInput = {}): Promise<JsonObject> {
    return this.request("GET", "/timegraph/conflicts", { params: optionalParams(input) });
  }

  async getImpactCapabilities(): Promise<JsonObject> {
    return this.request("GET", "/impact/capabilities");
  }

  async diffReleasesForImpact(input: ImpactReleaseDiffInput = {}): Promise<JsonObject> {
    return this.request("POST", "/impact/diff-releases", {
      json: {
        from_release_id: input.from_release_id ?? "parva-bs-public-demo",
        to_release_id: input.to_release_id ?? "parva-bs-public-demo",
        include_fixture: input.include_fixture ?? false,
      },
    });
  }

  async simulateChangeSet(input: ImpactChangeSetInput): Promise<JsonObject> {
    const { change_set, limit, ...changeSet } = input;
    return this.request("POST", "/impact/simulate-change-set", {
      json: { change_set: change_set ?? changeSet, limit },
    });
  }

  async simulateReleaseDiff(input: ImpactReleaseDiffInput = {}): Promise<JsonObject> {
    return this.request("POST", "/impact/simulate-release-diff", {
      json: {
        from_release_id: input.from_release_id ?? "parva-bs-public-demo",
        to_release_id: input.to_release_id ?? "parva-bs-public-demo",
        include_fixture: input.include_fixture ?? false,
        limit: input.limit ?? 100,
      },
    });
  }

  async getImpactRun(impactRunId: string): Promise<JsonObject> {
    return this.request("GET", `/impact/runs/${encodeURIComponent(impactRunId)}`);
  }

  async listImpactReasonCodes(): Promise<JsonObject> {
    return this.request("GET", "/impact/reason-codes");
  }

  async listImpactRecommendedActions(): Promise<JsonObject> {
    return this.request("GET", "/impact/recommended-actions");
  }

  async getImpactEventSchema(): Promise<JsonObject> {
    return this.request("GET", "/impact/event-schema");
  }

  async getAgentCapabilities(): Promise<JsonObject> {
    return this.request("GET", "/agent/capabilities");
  }

  async listAgentTools(): Promise<JsonObject> {
    return this.request("GET", "/agent/tools");
  }

  async getAgentManifest(): Promise<JsonObject> {
    return this.request("GET", "/agent/manifest");
  }

  async resolveTemporalIntent(text: string, context: JsonObject = {}): Promise<JsonObject> {
    return this.request("POST", "/agent/resolve-intent", { json: { text, context } });
  }

  async verifyTemporalClaim(input: AgentClaimInput): Promise<JsonObject> {
    return this.request("POST", "/agent/verify-claim", { json: input });
  }

  async planSchedule(input: AgentScheduleInput): Promise<JsonObject> {
    return this.request("POST", "/agent/plan-schedule", { json: input });
  }

  async explainTemporalDecision(payload: JsonObject): Promise<JsonObject> {
    return this.request("POST", "/agent/explain", { json: { payload } });
  }

  async checkHumanReview(payload: JsonObject): Promise<JsonObject> {
    return this.request("POST", "/agent/check-human-review", { json: { payload } });
  }

  async draftRule(text: string, profileId = "nepal_private_company_default"): Promise<JsonObject> {
    return this.request("POST", "/agent/draft-rule", { json: { text, profile_id: profileId } });
  }

  async runAgentTool(input: AgentRunToolInput): Promise<JsonObject> {
    return this.request("POST", "/agent/run-tool", { json: input });
  }

  async getProtocolVersion(): Promise<JsonObject> {
    return this.request("GET", "/protocol/version");
  }

  async getProtocolCapabilities(): Promise<JsonObject> {
    return this.request("GET", "/protocol/capabilities");
  }

  async listProtocolSpecs(): Promise<JsonObject> {
    return this.request("GET", "/protocol/specs");
  }

  async listProtocolSchemas(): Promise<JsonObject> {
    return this.request("GET", "/protocol/schemas");
  }

  async listCompatibilityLevels(): Promise<JsonObject> {
    return this.request("GET", "/protocol/compatibility-levels");
  }

  async runConformance(input: ProtocolConformanceInput = {}): Promise<JsonObject> {
    return this.request("POST", "/protocol/conformance/run", { json: input });
  }

  async issueCalendarCredential(input: ProtocolCredentialIssueInput): Promise<JsonObject> {
    return this.request("POST", "/protocol/credentials/issue", { json: input });
  }

  async verifyCalendarCredential(credential: JsonObject): Promise<JsonObject> {
    return this.request("POST", "/protocol/credentials/verify", { json: { credential } });
  }

  async getOfflineBundleManifest(): Promise<JsonObject> {
    return this.request("GET", "/protocol/offline-bundle/manifest");
  }

  async getFutureBsCapabilities(): Promise<JsonObject> {
    return this.requestAbsolute("GET", this.futureBsCapabilitiesUrl);
  }

  async getFutureBsMethodology(): Promise<JsonObject> {
    return this.requestAbsolute(
      "GET",
      buildFutureBsUrl(this.futureBsCapabilitiesUrl, "methodology"),
    );
  }

  async getFutureBsForecast(bsYear: number): Promise<JsonObject> {
    if (!Number.isInteger(bsYear) || bsYear <= 0) {
      throw new ParvaApiError("bsYear must be a positive integer");
    }
    return this.requestAbsolute(
      "GET",
      buildFutureBsUrl(this.futureBsCapabilitiesUrl, `forecast/${bsYear}`),
    );
  }

  private async request(
    method: "GET" | "POST",
    path: string,
    options: { params?: Record<string, string>; json?: unknown } = {},
  ): Promise<JsonObject> {
    const url = buildUrl(this.baseUrl, path, options.params);
    return this.requestAbsolute(method, url, options.json);
  }

  private async requestAbsolute(
    method: "GET" | "POST",
    url: string,
    jsonBody?: unknown,
  ): Promise<JsonObject> {
    for (let attempt = 0; attempt <= this.maxRetries; attempt += 1) {
      try {
        return await this.requestOnce(method, url, jsonBody);
      } catch (error) {
        if (!isRetryable(error) || attempt >= this.maxRetries) {
          throw error;
        }
        await this.sleep(retryDelayMs(error, attempt, this.retryBaseDelayMs));
      }
    }
    throw new ParvaApiError("Parva API request failed after retry attempts");
  }

  private async requestOnce(
    method: "GET" | "POST",
    url: string,
    jsonBody?: unknown,
  ): Promise<JsonObject> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeoutMs);
    try {
      const headers: Record<string, string> = { Accept: "application/json" };
      let body: string | undefined;
      if (jsonBody !== undefined) {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(jsonBody);
      }
      const response = await this.fetchImpl(url, {
        method,
        headers,
        body,
        signal: controller.signal,
      });
      const text = await response.text();
      const parsed = parseJsonSafely(text);
      if (!response.ok) {
        const detail = extractErrorDetail(parsed) ?? response.statusText;
        const retryAfterMs = parseRetryAfterMs(response.headers?.get("Retry-After") ?? null);
        throw new ParvaApiError(
          `Parva API request failed with status ${response.status}: ${detail}`,
          response.status,
          parsed ?? text,
          retryAfterMs,
        );
      }
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
        throw new ParvaApiError("Parva API returned a non-object JSON payload", response.status, parsed);
      }
      return parsed as JsonObject;
    } catch (error) {
      if (error instanceof ParvaApiError) {
        throw error;
      }
      if (error instanceof Error && error.name === "AbortError") {
        throw new ParvaApiError(`Parva API request timed out after ${this.timeoutMs}ms`);
      }
      const message = error instanceof Error ? error.message : String(error);
      throw new ParvaApiError(`Parva API request failed: ${message}`);
    } finally {
      clearTimeout(timeout);
    }
  }
}

const RETRYABLE_STATUSES = new Set([429, 500, 502, 503, 504]);

function isRetryable(error: unknown): boolean {
  return error instanceof ParvaApiError && RETRYABLE_STATUSES.has(error.status ?? 0);
}

function retryDelayMs(error: unknown, attempt: number, baseDelayMs: number): number {
  if (error instanceof ParvaApiError && error.status === 429 && error.retryAfterMs !== undefined) {
    return error.retryAfterMs;
  }
  const jitter = baseDelayMs > 0 ? Math.floor(Math.random() * baseDelayMs) : 0;
  return baseDelayMs * 2 ** attempt + jitter;
}

function parseRetryAfterMs(value: string | null): number | undefined {
  if (!value) {
    return undefined;
  }
  const seconds = Number(value);
  if (!Number.isFinite(seconds)) {
    return undefined;
  }
  return Math.max(0, seconds * 1000);
}

function sleepMs(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function getToday(options: { riskMode?: string } = {}, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getToday(options);
}

export function adToBs(date: string, clientOptions?: ParvaClientOptions, options: { proof?: ProofMode } = {}) {
  return new ParvaClient(clientOptions).adToBs(date, options);
}

export function bsToAd(input: BsDateInput & { proof?: ProofMode }, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).bsToAd(input);
}

export function validateBsDate(input: BsDateInput & { proof?: ProofMode }, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).validateBsDate(input);
}

export function getMonthCalendar(year: number, month: number, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getMonthCalendar(year, month);
}

export function getFiscalYear(bsYear: number, clientOptions?: ParvaClientOptions, options: { proof?: ProofMode } = {}) {
  return new ParvaClient(clientOptions).getFiscalYear(bsYear, options);
}

export function getBsMonths(
  bsYear: number,
  clientOptions?: ParvaClientOptions,
  options: { mode?: "canonical" | "solar_civil" | "static_lookup" | "compare"; proof?: ProofMode } = {},
) {
  return new ParvaClient(clientOptions).getBsMonths(bsYear, options);
}

export function getBusinessDays(input: BusinessDaysInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getBusinessDays(input);
}

export function getEnterpriseCapabilities(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getEnterpriseCapabilities();
}

export function listProfiles(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listProfiles();
}

export function getProfile(profileId: string, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getProfile(profileId);
}

export function evaluateDate(input: ComplianceDateInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).evaluateDate(input);
}

export function checkHoliday(input: HolidayInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).checkHoliday(input);
}

export function nextWorkingDay(input: WorkingDaySearchInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).nextWorkingDay(input);
}

export function previousWorkingDay(input: WorkingDaySearchInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).previousWorkingDay(input);
}

export function addWorkingDays(input: AddWorkingDaysInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).addWorkingDays(input);
}

export function monthClosingDay(input: MonthClosingDayInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).monthClosingDay(input);
}

export function fiscalPeriod(input: ComplianceDateInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).fiscalPeriod(input);
}

export function getPolicy(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getPolicy();
}

export function getTrustCapabilities(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getTrustCapabilities();
}

export function listSources(input: TrustReleaseInput = {}, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listSources(input);
}

export function getSource(
  sourceId: string,
  input: TrustReleaseInput = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).getSource(sourceId, input);
}

export function listReleases(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listReleases();
}

export function getRelease(releaseId: string, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getRelease(releaseId);
}

export function diffReleases(
  fromRelease: string,
  toRelease: string,
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).diffReleases(fromRelease, toRelease);
}

export function getTrustLog(input: TrustReleaseInput = {}, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getTrustLog(input);
}

export function createDateConversionEvidence(
  input: DateConversionEvidenceInput,
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).createDateConversionEvidence(input);
}

export function createComplianceDecisionEvidence(
  input: ComplianceEvidenceInput,
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).createComplianceDecisionEvidence(input);
}

export function getTimeGraphCapabilities(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getTimeGraphCapabilities();
}

export function getRuleCapabilities(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getRuleCapabilities();
}

export function listRules(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listRules();
}

export function getRule(ruleId: string, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getRule(ruleId);
}

export function validateRule(rule: JsonObject, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).validateRule(rule);
}

export function evaluateRule(
  ruleId: string,
  input: RuleEvaluateInput = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).evaluateRule(ruleId, input);
}

export function testRule(ruleId: string, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).testRule(ruleId);
}

export function evaluateCustomRule(input: CustomRuleEvaluateInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).evaluateCustomRule(input);
}

export function explainRule(input: RuleExplainInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).explainRule(input);
}

export function listFacts(input: TimeGraphQueryInput = {}, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listFacts(input);
}

export function getFact(
  factId: string,
  input: TrustReleaseInput = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).getFact(factId, input);
}

export function queryFacts(input: TimeGraphQueryInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).queryFacts(input);
}

export function getFactsForDate(
  calendar: string,
  date: string,
  input: TimeGraphListInput = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).getFactsForDate(calendar, date, input);
}

export function getFactsForSource(
  sourceId: string,
  input: TimeGraphListInput = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).getFactsForSource(sourceId, input);
}

export function getFactsForRelease(
  releaseId: string,
  input: TimeGraphListInput = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).getFactsForRelease(releaseId, input);
}

export function getFactsForProfile(
  profileId: string,
  input: TimeGraphListInput = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).getFactsForProfile(profileId, input);
}

export function getRelationships(
  entityId: string,
  input: TimeGraphListInput = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).getRelationships(entityId, input);
}

export function traceFact(
  factId: string,
  input: TrustReleaseInput & { depth?: number } = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).traceFact(factId, input);
}

export function listConflicts(input: TimeGraphListInput = {}, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listConflicts(input);
}

export function getImpactCapabilities(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getImpactCapabilities();
}

export function diffReleasesForImpact(
  input: ImpactReleaseDiffInput = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).diffReleasesForImpact(input);
}

export function simulateChangeSet(input: ImpactChangeSetInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).simulateChangeSet(input);
}

export function simulateReleaseDiff(
  input: ImpactReleaseDiffInput = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).simulateReleaseDiff(input);
}

export function getImpactRun(impactRunId: string, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getImpactRun(impactRunId);
}

export function listImpactReasonCodes(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listImpactReasonCodes();
}

export function listImpactRecommendedActions(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listImpactRecommendedActions();
}

export function getImpactEventSchema(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getImpactEventSchema();
}

export function getAgentCapabilities(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getAgentCapabilities();
}

export function listAgentTools(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listAgentTools();
}

export function getAgentManifest(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getAgentManifest();
}

export function resolveTemporalIntent(
  text: string,
  context: JsonObject = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).resolveTemporalIntent(text, context);
}

export function verifyTemporalClaim(input: AgentClaimInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).verifyTemporalClaim(input);
}

export function planSchedule(input: AgentScheduleInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).planSchedule(input);
}

export function explainTemporalDecision(payload: JsonObject, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).explainTemporalDecision(payload);
}

export function checkHumanReview(payload: JsonObject, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).checkHumanReview(payload);
}

export function draftRule(
  text: string,
  profileId = "nepal_private_company_default",
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).draftRule(text, profileId);
}

export function runAgentTool(input: AgentRunToolInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).runAgentTool(input);
}

export function getProtocolVersion(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getProtocolVersion();
}

export function getProtocolCapabilities(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getProtocolCapabilities();
}

export function listProtocolSpecs(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listProtocolSpecs();
}

export function listProtocolSchemas(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listProtocolSchemas();
}

export function listCompatibilityLevels(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).listCompatibilityLevels();
}

export function runConformance(
  input: ProtocolConformanceInput = {},
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).runConformance(input);
}

export function issueCalendarCredential(
  input: ProtocolCredentialIssueInput,
  clientOptions?: ParvaClientOptions,
) {
  return new ParvaClient(clientOptions).issueCalendarCredential(input);
}

export function verifyCalendarCredential(credential: JsonObject, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).verifyCalendarCredential(credential);
}

export function getOfflineBundleManifest(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getOfflineBundleManifest();
}

export function getFutureBsCapabilities(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getFutureBsCapabilities();
}

export function getFutureBsMethodology(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getFutureBsMethodology();
}

export function getFutureBsForecast(bsYear: number, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getFutureBsForecast(bsYear);
}
