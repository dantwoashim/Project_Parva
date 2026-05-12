export const DEFAULT_API_BASE = "https://api.prabinghimire1.com.np/v3/api";
export const DEFAULT_FUTURE_BS_CAPABILITIES_URL =
  "https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities";

export type JsonObject = Record<string, unknown>;

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
}

export interface ValidateBsDateResult {
  valid: boolean;
  publication_status: "computed_prediction_not_official";
  result?: JsonObject;
  error?: string;
}

export class ParvaApiError extends Error {
  readonly status?: number;
  readonly body?: unknown;

  constructor(message: string, status?: number, body?: unknown) {
    super(message);
    this.name = "ParvaApiError";
    this.status = status;
    this.body = body;
  }
}

export class ParvaClient {
  readonly baseUrl: string;
  readonly futureBsCapabilitiesUrl: string;
  readonly timeoutMs: number;
  private readonly fetchImpl: typeof fetch;

  constructor(options: ParvaClientOptions = {}) {
    this.baseUrl = trimTrailingSlash(options.baseUrl ?? DEFAULT_API_BASE);
    this.futureBsCapabilitiesUrl =
      options.futureBsCapabilitiesUrl ?? DEFAULT_FUTURE_BS_CAPABILITIES_URL;
    this.timeoutMs = options.timeoutMs ?? 10_000;
    this.fetchImpl = options.fetchImpl ?? globalThis.fetch;
    if (!this.fetchImpl) {
      throw new ParvaApiError("No fetch implementation is available for ParvaClient");
    }
  }

  async getToday(options: { riskMode?: string } = {}): Promise<JsonObject> {
    const params = options.riskMode ? { risk_mode: options.riskMode } : undefined;
    return this.request("GET", "/calendar/today", { params });
  }

  async adToBs(date: string): Promise<JsonObject> {
    return this.request("GET", "/calendar/convert", { params: { date } });
  }

  async bsToAd(input: BsDateInput): Promise<JsonObject> {
    return this.request("POST", "/calendar/bs-to-gregorian", { json: input });
  }

  async validateBsDate(input: BsDateInput): Promise<ValidateBsDateResult> {
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

  async getFutureBsCapabilities(): Promise<JsonObject> {
    return this.requestAbsolute("GET", this.futureBsCapabilitiesUrl);
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
        throw new ParvaApiError(
          `Parva API request failed with status ${response.status}: ${detail}`,
          response.status,
          parsed ?? text,
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

export function getToday(options: { riskMode?: string } = {}, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getToday(options);
}

export function adToBs(date: string, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).adToBs(date);
}

export function bsToAd(input: BsDateInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).bsToAd(input);
}

export function validateBsDate(input: BsDateInput, clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).validateBsDate(input);
}

export function getFutureBsCapabilities(clientOptions?: ParvaClientOptions) {
  return new ParvaClient(clientOptions).getFutureBsCapabilities();
}

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

function buildUrl(baseUrl: string, path: string, params?: Record<string, string>): string {
  const normalizedPath = path.replace(/^\/+/, "");
  const url = new URL(`${trimTrailingSlash(baseUrl)}/${normalizedPath}`);
  for (const [key, value] of Object.entries(params ?? {})) {
    url.searchParams.set(key, value);
  }
  return url.toString();
}

function parseJsonSafely(text: string): unknown {
  if (!text.trim()) {
    return {};
  }
  try {
    return JSON.parse(text);
  } catch {
    return undefined;
  }
}

function extractErrorDetail(payload: unknown): string | undefined {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return undefined;
  }
  const detail = (payload as Record<string, unknown>).detail;
  if (typeof detail === "string") {
    return detail;
  }
  return undefined;
}
