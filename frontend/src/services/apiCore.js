import { ensureApiEnvelope } from './apiContracts';

const API_BASE = import.meta.env.VITE_API_BASE || '/v3/api';
const DEFAULT_REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 10000);
const ENVELOPE_HEADER_NAME = 'X-Parva-Envelope';
const ENVELOPE_HEADER_VALUE = 'data-meta';

export class ParvaApiError extends Error {
  constructor(message, { status, statusText, detail, requestId, errors, payload } = {}) {
    super(message);
    this.name = 'ParvaApiError';
    this.status = status;
    this.statusText = statusText;
    this.detail = detail;
    this.requestId = requestId || null;
    this.errors = errors || null;
    this.payload = payload || null;
  }
}

function normalizeRequestId(value) {
  if (typeof value === 'string' && value.trim()) {
    return value.trim();
  }
  return null;
}

function extractRequestId(response, payload = null) {
  return normalizeRequestId(payload?.request_id)
    || normalizeRequestId(payload?.requestId)
    || normalizeRequestId(payload?.meta?.request_id)
    || normalizeRequestId(payload?.meta?.requestId)
    || normalizeRequestId(response?.headers?.get?.('x-request-id'))
    || null;
}

function attachRequestId(error, requestId) {
  if (error instanceof ParvaApiError && requestId && !error.requestId) {
    error.requestId = requestId;
  }
  return error;
}

async function parseErrorPayload(response) {
  const contentType = response.headers.get('content-type') || '';

  try {
    if (contentType.includes('application/json')) {
      return await response.json();
    }

    const text = await response.text();
    return text ? { detail: text } : null;
  } catch {
    return null;
  }
}

export function normalizeCoordinateField(value) {
  if (value === undefined || value === null) return value;
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : value;
  if (typeof value === 'string') return value.trim();
  return value;
}

function normalizePrivatePayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return payload;
  }

  const normalized = { ...payload };
  for (const key of ['lat', 'lon']) {
    if (key in normalized) {
      normalized[key] = normalizeCoordinateField(normalized[key]);
    }
  }
  return normalized;
}

export function createPrivateJsonOptions(payload, options = {}) {
  const normalizedPayload = normalizePrivatePayload(payload);
  return {
    method: 'POST',
    cache: 'no-store',
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    body: JSON.stringify(normalizedPayload),
  };
}

function normalizeTimeoutMs(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return DEFAULT_REQUEST_TIMEOUT_MS;
  }
  return parsed;
}

function createRequestSignal({ timeoutMs, signal: upstreamSignal } = {}) {
  const controller = new AbortController();
  const resolvedTimeoutMs = normalizeTimeoutMs(timeoutMs);
  let abortedByTimeout = false;
  let upstreamAbortHandler = null;

  if (upstreamSignal) {
    if (upstreamSignal.aborted) {
      controller.abort(upstreamSignal.reason);
    } else {
      upstreamAbortHandler = () => controller.abort(upstreamSignal.reason);
      upstreamSignal.addEventListener('abort', upstreamAbortHandler, { once: true });
    }
  }

  const timeoutId = window.setTimeout(() => {
    abortedByTimeout = true;
    controller.abort(new DOMException(`Request timed out after ${resolvedTimeoutMs}ms`, 'TimeoutError'));
  }, resolvedTimeoutMs);

  return {
    signal: controller.signal,
    timeoutMs: resolvedTimeoutMs,
    didTimeout: () => abortedByTimeout,
    cleanup() {
      window.clearTimeout(timeoutId);
      if (upstreamSignal && upstreamAbortHandler) {
        upstreamSignal.removeEventListener('abort', upstreamAbortHandler);
      }
    },
  };
}

export function ensureJsonPayload(payload, endpoint) {
  if (payload != null && typeof payload === 'object') {
    return payload;
  }
  throw new ParvaApiError(`Unexpected response shape for ${endpoint}`, {
    status: 502,
    detail: 'Upstream response did not match the expected JSON contract.',
    payload,
  });
}

function buildMetaEnvelope(payload) {
  const metadataSource = payload && typeof payload === 'object' && !Array.isArray(payload)
    ? payload
    : {};
  return {
    data: payload,
    meta: {
      confidence: metadataSource.confidence || 'unknown',
      method: metadataSource.method || 'unknown',
      provenance: metadataSource.provenance || {},
      uncertainty: metadataSource.uncertainty || { boundary_risk: 'unknown', interval_hours: null },
      trace_id: metadataSource.calculation_trace_id || metadataSource.trace_id || null,
      policy: metadataSource.policy || { profile: 'np-mainstream', jurisdiction: 'NP', advisory: true },
      degraded: metadataSource.degraded || { active: false, reasons: [], defaults_applied: [] },
    },
  };
}

export async function fetchAPI(endpoint, options = {}, parseAs = 'json') {
  const envelope = await fetchAPIEnvelope(endpoint, options, parseAs);
  if (parseAs === 'text') return envelope;
  return envelope.data;
}

export async function fetchAPIEnvelope(endpoint, options = {}, parseAs = 'json') {
  const url = `${API_BASE}${endpoint}`;
  const {
    timeoutMs,
    signal: upstreamSignal,
    preferEnvelope = false,
    headers: requestHeaders,
    ...fetchOptions
  } = options;
  const hasBody = fetchOptions.body !== undefined;
  const requestSignal = createRequestSignal({ timeoutMs, signal: upstreamSignal });

  let response;
  try {
    response = await fetch(url, {
      ...fetchOptions,
      signal: requestSignal.signal,
      headers: {
        ...(hasBody && parseAs === 'json' ? { 'Content-Type': 'application/json' } : {}),
        ...(preferEnvelope && parseAs === 'json' ? { [ENVELOPE_HEADER_NAME]: ENVELOPE_HEADER_VALUE } : {}),
        ...requestHeaders,
      },
    });
  } catch (error) {
    requestSignal.cleanup();
    if (requestSignal.signal.aborted) {
      const didTimeout = requestSignal.didTimeout() || error?.name === 'TimeoutError';
      throw new ParvaApiError(
        didTimeout
          ? `Request timed out after ${requestSignal.timeoutMs}ms`
          : 'Request was cancelled',
        {
          status: didTimeout ? 408 : 499,
          detail: didTimeout ? 'Request timeout exceeded' : 'Request cancelled',
          payload: null,
        },
      );
    }
    throw error;
  }

  try {
    if (!response.ok) {
      const errorPayload = await parseErrorPayload(response);
      const detail = errorPayload?.detail || errorPayload?.message || `${response.status} ${response.statusText}`;
      throw new ParvaApiError(detail, {
        status: response.status,
        statusText: response.statusText,
        detail: errorPayload?.detail || null,
        requestId: extractRequestId(response, errorPayload),
        errors: errorPayload?.errors || null,
        payload: errorPayload,
      });
    }

    if (parseAs === 'text') {
      return response.text();
    }

    let payload;
    try {
      payload = ensureJsonPayload(await response.json(), endpoint);
    } catch (error) {
      throw attachRequestId(error, extractRequestId(response));
    }

    const requestId = extractRequestId(response, payload);
    if (payload && typeof payload === 'object' && !Array.isArray(payload) && 'data' in payload && 'meta' in payload) {
      const envelope = ensureApiEnvelope(endpoint, payload);
      if (requestId && !envelope.meta.request_id) {
        envelope.meta.request_id = requestId;
      }
      return envelope;
    }
    if (preferEnvelope) {
      throw new ParvaApiError(`Unexpected response shape for ${endpoint}`, {
        status: 502,
        detail: `${endpoint} did not honor the requested data-meta envelope contract.`,
        requestId,
        payload,
      });
    }

    const envelope = buildMetaEnvelope(payload);
    if (requestId) {
      envelope.meta.request_id = requestId;
    }
    return envelope;
  } finally {
    requestSignal.cleanup();
  }
}

export function getApiBase() {
  return API_BASE;
}
