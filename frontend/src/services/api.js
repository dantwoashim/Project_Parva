/**
 * API Service
 * ==========
 * Public profile defaults to v3.
 */

import {
  ensureApiEnvelope,
  normalizeCalendarTodayPayload,
  normalizeFestivalDetailEnvelope,
  normalizeFestivalTimelineEnvelope,
  normalizeKundaliGraphEnvelope,
  normalizeMuhurtaHeatmapEnvelope,
  normalizePersonalContextEnvelope,
  normalizePersonalPanchangaEnvelope,
  normalizeTemporalCompassEnvelope,
} from './apiContracts';

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

function normalizeCoordinateField(value) {
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

function createPrivateJsonOptions(payload, options = {}) {
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

export function ensureJsonObjectPayload(payload, endpoint) {
  if (payload && typeof payload === 'object' && !Array.isArray(payload)) {
    return payload;
  }
  throw new ParvaApiError(`Unexpected response shape for ${endpoint}`, {
    status: 502,
    detail: 'Upstream response did not match the expected JSON object contract.',
    payload,
  });
}

function buildMetaEnvelope(payload) {
  return {
    data: payload,
    meta: {
      confidence: payload?.confidence || 'unknown',
      method: payload?.method || 'unknown',
      provenance: payload?.provenance || {},
      uncertainty: payload?.uncertainty || { boundary_risk: 'unknown', interval_hours: null },
      trace_id: payload?.calculation_trace_id || payload?.trace_id || null,
      policy: payload?.policy || { profile: 'np-mainstream', jurisdiction: 'NP', advisory: true },
      degraded: payload?.degraded || { active: false, reasons: [], defaults_applied: [] },
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
      payload = ensureJsonObjectPayload(await response.json(), endpoint);
    } catch (error) {
      throw attachRequestId(error, extractRequestId(response));
    }

    const requestId = extractRequestId(response, payload);
    if ('data' in payload && 'meta' in payload) {
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

export const temporalAPI = {
  getCompass: ({ date, lat, lon, tz, qualityBand = 'computed' } = {}) =>
    fetchAPI('/temporal/compass', createPrivateJsonOptions({
      date,
      lat,
      lon,
      tz,
      quality_band: qualityBand,
    })),
  getCompassEnvelope: ({ date, lat, lon, tz, qualityBand = 'computed' } = {}) =>
    fetchAPIEnvelope('/temporal/compass', {
      ...createPrivateJsonOptions({
        date,
        lat,
        lon,
        tz,
        quality_band: qualityBand,
      }),
      preferEnvelope: true,
    }).then(normalizeTemporalCompassEnvelope),
};

export const glossaryAPI = {
  get: ({ domain, lang = 'en' } = {}) => fetchAPI(`/glossary?domain=${domain}&lang=${lang}`),
};

export const festivalAPI = {
  getAll: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetchAPI(`/festivals${query ? `?${query}` : ''}`);
  },
  getCoverageScoreboard: (target = 300) => fetchAPI(`/festivals/coverage/scoreboard?target_rules=${target}`),
  getUpcoming: (days = 90, qualityBand = 'computed') => fetchAPI(`/festivals/upcoming?days=${days}&quality_band=${qualityBand}`),
  getTimeline: ({ from, to, qualityBand = 'computed', category, region, search, sort, lang = 'en' } = {}) => {
    const params = new URLSearchParams({ from, to, quality_band: qualityBand, lang });
    if (category) params.set('category', category);
    if (region) params.set('region', region);
    if (search) params.set('search', search);
    if (sort) params.set('sort', sort);
    return fetchAPI(`/festivals/timeline?${params.toString()}`);
  },
  getTimelineEnvelope: ({ from, to, qualityBand = 'computed', category, region, search, sort, lang = 'en' } = {}) => {
    const params = new URLSearchParams({ from, to, quality_band: qualityBand, lang });
    if (category) params.set('category', category);
    if (region) params.set('region', region);
    if (search) params.set('search', search);
    if (sort) params.set('sort', sort);
    return fetchAPIEnvelope(`/festivals/timeline?${params.toString()}`, { preferEnvelope: true }).then(normalizeFestivalTimelineEnvelope);
  },
  getById: (id, year) => {
    const query = year ? `?year=${year}` : '';
    return fetchAPI(`/festivals/${id}${query}`);
  },
  getByIdEnvelope: (id, year) => {
    const query = year ? `?year=${year}` : '';
    return fetchAPIEnvelope(`/festivals/${id}${query}`, { preferEnvelope: true }).then(normalizeFestivalDetailEnvelope);
  },
  getExplain: (id, year) => {
    const query = year ? `?year=${year}` : '';
    return fetchAPI(`/festivals/${id}/explain${query}`);
  },
  getTrace: (traceId) => fetchAPI(`/explain/${traceId}`),
  getDates: (id, years = 3) => fetchAPI(`/festivals/${id}/dates?years=${years}`),
  getOnDate: (date) => fetchAPI(`/festivals/on-date/${date}`),
};

export const calendarAPI = {
  getMonth: (year, month) => fetchAPI(`/festivals/calendar/${year}/${month}`),
  getDualMonth: (year, month) => fetchAPI(`/calendar/dual-month?year=${year}&month=${month}`),
  getToday: async () => normalizeCalendarTodayPayload(await fetchAPI('/calendar/today')),
  getPanchanga: (date) => fetchAPI(`/calendar/panchanga?date=${date}`),
  getPanchangaEnvelope: (date) => fetchAPIEnvelope(`/calendar/panchanga?date=${date}`),
  getTithi: (date, latitude, longitude) => {
    const params = new URLSearchParams({ date });
    if (latitude !== undefined) params.set('latitude', latitude);
    if (longitude !== undefined) params.set('longitude', longitude);
    return fetchAPI(`/calendar/tithi?${params.toString()}`);
  },
  getResolveEnvelope: (date, options = {}) => {
    const params = new URLSearchParams({ date });
    if (options.profile) params.set('profile', options.profile);
    if (options.latitude !== undefined) params.set('latitude', options.latitude);
    if (options.longitude !== undefined) params.set('longitude', options.longitude);
    if (options.include_trace !== undefined) params.set('include_trace', options.include_trace);
    return fetchAPIEnvelope(`/resolve?${params.toString()}`);
  },
};

export const personalAPI = {
  getPanchanga: ({ date, lat, lon, tz } = {}) =>
    fetchAPI('/personal/panchanga', createPrivateJsonOptions({ date, lat, lon, tz })),
  getPanchangaEnvelope: ({ date, lat, lon, tz } = {}) =>
    fetchAPIEnvelope('/personal/panchanga', {
      ...createPrivateJsonOptions({ date, lat, lon, tz }),
      preferEnvelope: true,
    }).then(normalizePersonalPanchangaEnvelope),
  getContext: ({ date, lat, lon, tz } = {}) =>
    fetchAPI('/personal/context', createPrivateJsonOptions({ date, lat, lon, tz })),
  getContextEnvelope: ({ date, lat, lon, tz } = {}) =>
    fetchAPIEnvelope('/personal/context', {
      ...createPrivateJsonOptions({ date, lat, lon, tz }),
      preferEnvelope: true,
    }).then(normalizePersonalContextEnvelope),
};

export const muhurtaAPI = {
  getDay: ({ date, lat, lon, tz, birthNakshatra } = {}) =>
    fetchAPI('/muhurta', createPrivateJsonOptions({
      date,
      lat,
      lon,
      tz,
      birth_nakshatra: birthNakshatra,
    })),
  getAuspicious: ({ date, type = 'general', lat, lon, tz, birthNakshatra, assumptionSet = 'np-mainstream-v2' } = {}) =>
    fetchAPI('/muhurta/auspicious', createPrivateJsonOptions({
      date,
      type,
      lat,
      lon,
      tz,
      birth_nakshatra: birthNakshatra,
      assumption_set: assumptionSet,
    })),
  getRahuKalam: ({ date, lat, lon, tz } = {}) =>
    fetchAPI('/muhurta/rahu-kalam', createPrivateJsonOptions({ date, lat, lon, tz })),
  getHeatmap: ({ date, lat, lon, tz, type = 'general', assumptionSet = 'np-mainstream-v2' } = {}) =>
    fetchAPI('/muhurta/heatmap', createPrivateJsonOptions({
      date,
      lat,
      lon,
      tz,
      type,
      assumption_set: assumptionSet,
    })),
  getHeatmapEnvelope: ({ date, lat, lon, tz, type = 'general', assumptionSet = 'np-mainstream-v2' } = {}) =>
    fetchAPIEnvelope('/muhurta/heatmap', {
      ...createPrivateJsonOptions({
        date,
        lat,
        lon,
        tz,
        type,
        assumption_set: assumptionSet,
      }),
      preferEnvelope: true,
    }).then(normalizeMuhurtaHeatmapEnvelope),
};

export const kundaliAPI = {
  getKundali: ({ datetime, lat, lon, tz } = {}) =>
    fetchAPI('/kundali', createPrivateJsonOptions({ datetime, lat, lon, tz })),
  getLagna: ({ datetime, lat, lon, tz } = {}) =>
    fetchAPI('/kundali/lagna', createPrivateJsonOptions({ datetime, lat, lon, tz })),
  getGraph: ({ datetime, lat, lon, tz } = {}) =>
    fetchAPI('/kundali/graph', createPrivateJsonOptions({ datetime, lat, lon, tz })),
  getGraphEnvelope: ({ datetime, lat, lon, tz } = {}) =>
    fetchAPIEnvelope('/kundali/graph', {
      ...createPrivateJsonOptions({ datetime, lat, lon, tz }),
      preferEnvelope: true,
    }).then(normalizeKundaliGraphEnvelope),
};

export const feedAPI = {
  getAllLink: (years = 2, lang = 'en') => `${API_BASE}/feeds/all.ics?years=${years}&lang=${lang}`,
  getNationalLink: (years = 2, lang = 'en') => `${API_BASE}/feeds/national.ics?years=${years}&lang=${lang}`,
  getNewariLink: (years = 2, lang = 'en') => `${API_BASE}/feeds/newari.ics?years=${years}&lang=${lang}`,
  getCustomLink: (festivalIds = [], years = 2, lang = 'en') => {
    const festivals = encodeURIComponent(festivalIds.join(','));
    return `${API_BASE}/feeds/custom.ics?festivals=${festivals}&years=${years}&lang=${lang}`;
  },
  getPreview: (days = 30, lang = 'en') => fetchAPI(`/feeds/next?days=${days}&lang=${lang}`),
};

export default {
  temporal: temporalAPI,
  glossary: glossaryAPI,
  festivals: festivalAPI,
  calendar: calendarAPI,
  personal: personalAPI,
  muhurta: muhurtaAPI,
  kundali: kundaliAPI,
  feeds: feedAPI,
};
