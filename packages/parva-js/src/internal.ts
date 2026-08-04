export function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

export function buildFutureBsUrl(capabilitiesUrl: string, path: string): string {
  const base = trimTrailingSlash(capabilitiesUrl).replace(/\/capabilities$/, "");
  return `${base}/${path.replace(/^\/+/, "")}`;
}

export function buildUrl(
  baseUrl: string,
  path: string,
  params?: Record<string, string>,
): string {
  const normalizedPath = path.replace(/^\/+/, "");
  const url = new URL(`${trimTrailingSlash(baseUrl)}/${normalizedPath}`);
  for (const [key, value] of Object.entries(params ?? {})) {
    url.searchParams.set(key, value);
  }
  return url.toString();
}

export function optionalParams(params: object): Record<string, string> | undefined {
  const cleaned: Record<string, string> = {};
  for (const [key, value] of Object.entries(params)) {
    if (
      (typeof value === "string" || typeof value === "number" || typeof value === "boolean") &&
      value !== ""
    ) {
      cleaned[key] = String(value);
    }
  }
  return Object.keys(cleaned).length ? cleaned : undefined;
}

export function parseJsonSafely(text: string): unknown {
  if (!text.trim()) {
    return {};
  }
  try {
    return JSON.parse(text);
  } catch {
    return undefined;
  }
}

export function extractErrorDetail(payload: unknown): string | undefined {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return undefined;
  }
  const body = payload as Record<string, unknown>;
  const error = body.error;
  if (error && typeof error === "object" && !Array.isArray(error)) {
    const message = (error as Record<string, unknown>).message;
    if (typeof message === "string") {
      return message;
    }
  }
  const detail = body.detail;
  if (typeof detail === "string") {
    return detail;
  }
  return undefined;
}
