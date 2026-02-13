export type ParvaRequestParams = Record<string, string | number | boolean | undefined>;

export interface ConfidenceMeta {
  level: "official" | "computed" | "estimated" | "unknown";
  score: number;
}

export interface ProvenanceMeta {
  snapshot_id: string | null;
  dataset_hash: string | null;
  rules_hash: string | null;
  verify_url: string | null;
  signature: string | null;
}

export interface UncertaintyMeta {
  interval_hours: number | null;
  boundary_risk: "low" | "medium" | "high" | "unknown";
}

export interface PolicyMeta {
  profile: string;
  jurisdiction: string;
  advisory: boolean;
}

export interface ResponseMeta {
  confidence: ConfidenceMeta;
  method: string;
  provenance: ProvenanceMeta;
  uncertainty: UncertaintyMeta;
  trace_id: string | null;
  policy: PolicyMeta;
}

export interface DataEnvelope<T> {
  data: T;
  meta: ResponseMeta;
}

export interface ParvaClientOptions {
  baseUrl?: string;
  retries?: number;
  backoffMs?: number;
  fetchImpl?: typeof fetch;
}

export class ParvaClient {
  private readonly baseUrl: string;
  private readonly retries: number;
  private readonly backoffMs: number;
  private readonly fetchImpl: typeof fetch;

  constructor(options: ParvaClientOptions = {}) {
    this.baseUrl = (options.baseUrl ?? "http://localhost:8000/v5/api").replace(/\/$/, "");
    this.retries = Math.max(options.retries ?? 2, 0);
    this.backoffMs = Math.max(options.backoffMs ?? 250, 0);
    this.fetchImpl = options.fetchImpl ?? fetch;
  }

  private async get<T = Record<string, unknown>>(
    path: string,
    params?: ParvaRequestParams,
  ): Promise<DataEnvelope<T>> {
    const url = new URL(`${this.baseUrl}${path}`);
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) url.searchParams.set(k, String(v));
      });
    }

    let lastError: unknown = undefined;
    for (let attempt = 0; attempt <= this.retries; attempt += 1) {
      try {
        const resp = await this.fetchImpl(url.toString());
        if (!resp.ok) {
          if (resp.status >= 500 && attempt < this.retries) {
            await this.sleep(this.backoffMs * 2 ** attempt);
            continue;
          }
          throw new Error(`Parva API ${resp.status}: ${await resp.text()}`);
        }
        const payload = await resp.json();
        if (payload?.data !== undefined && payload?.meta !== undefined) {
          return payload as DataEnvelope<T>;
        }
        // v3 compatibility mode
        return {
          data: payload as T,
          meta: {
            confidence: { level: "unknown", score: 0.5 },
            method: "unknown",
            provenance: {
              snapshot_id: null,
              dataset_hash: null,
              rules_hash: null,
              verify_url: null,
              signature: null,
            },
            uncertainty: {
              interval_hours: null,
              boundary_risk: "unknown",
            },
            trace_id: null,
            policy: {
              profile: "np-mainstream",
              jurisdiction: "NP",
              advisory: true,
            },
          },
        };
      } catch (error) {
        lastError = error;
        if (attempt >= this.retries) {
          break;
        }
        await this.sleep(this.backoffMs * 2 ** attempt);
      }
    }
    throw lastError instanceof Error ? lastError : new Error("Request failed");
  }

  private async sleep(ms: number): Promise<void> {
    await new Promise((resolve) => setTimeout(resolve, ms));
  }

  today() {
    return this.get("/calendar/today");
  }

  convert(date: string) {
    return this.get("/calendar/convert", { date });
  }

  panchanga(date?: string) {
    return this.get("/calendar/panchanga", date ? { date } : undefined);
  }

  upcoming(days = 30) {
    return this.get("/festivals/upcoming", { days });
  }

  observances(date: string, location = "kathmandu", preferences?: string) {
    return this.get("/observances", { date, location, preferences });
  }

  explainFestival(festivalId: string, year: number) {
    return this.get(`/festivals/${festivalId}/explain`, { year });
  }

  explainTrace(traceId: string) {
    return this.get(`/explain/${traceId}`);
  }

  resolve(date: string, options?: { profile?: string; latitude?: number; longitude?: number; includeTrace?: boolean }) {
    return this.get("/resolve", {
      date,
      profile: options?.profile ?? "np-mainstream",
      latitude: options?.latitude ?? 27.7172,
      longitude: options?.longitude ?? 85.324,
      include_trace: options?.includeTrace ?? true,
    });
  }

  specConformance() {
    return this.get("/spec/conformance");
  }

  verifyTrace(traceId: string) {
    return this.get(`/provenance/verify/trace/${traceId}`);
  }
}
