/**
 * API Service
 * ==========
 * Public profile defaults to v3.
 */

const API_BASE = import.meta.env.VITE_API_BASE || '/v3/api';

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

export async function fetchAPI(endpoint, options = {}, parseAs = 'json') {
  const envelope = await fetchAPIEnvelope(endpoint, options, parseAs);
  if (parseAs === 'text') return envelope;
  return envelope.data;
}

export async function fetchAPIEnvelope(endpoint, options = {}, parseAs = 'json') {
  const url = `${API_BASE}${endpoint}`;
  const hasBody = options.body !== undefined;
  const response = await fetch(url, {
    headers: {
      ...(hasBody && parseAs === 'json' ? { 'Content-Type': 'application/json' } : {}),
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorPayload = await parseErrorPayload(response);
    const detail = errorPayload?.detail || errorPayload?.message || `${response.status} ${response.statusText}`;
    throw new ParvaApiError(detail, {
      status: response.status,
      statusText: response.statusText,
      detail: errorPayload?.detail || null,
      requestId: errorPayload?.request_id || null,
      errors: errorPayload?.errors || null,
      payload: errorPayload,
    });
  }

  if (parseAs === 'text') {
    return response.text();
  }

  const payload = await response.json();
  if (payload && typeof payload === 'object' && 'data' in payload && 'meta' in payload) {
    return payload;
  }

  return {
    data: payload,
    meta: {
      confidence: payload?.confidence || 'unknown',
      method: payload?.method || 'unknown',
      provenance: payload?.provenance || {},
      uncertainty: payload?.uncertainty || { boundary_risk: 'unknown', interval_hours: null },
      trace_id: payload?.calculation_trace_id || payload?.trace_id || null,
      policy: payload?.policy || { profile: 'np-mainstream', jurisdiction: 'NP', advisory: true },
    },
  };
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
    fetchAPIEnvelope('/temporal/compass', createPrivateJsonOptions({
      date,
      lat,
      lon,
      tz,
      quality_band: qualityBand,
    })),
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
  getTimeline: ({ from, to, qualityBand = 'computed', category, region, search, lang = 'en' } = {}) => {
    const params = new URLSearchParams({ from, to, quality_band: qualityBand, lang });
    if (category) params.set('category', category);
    if (region) params.set('region', region);
    if (search) params.set('search', search);
    return fetchAPI(`/festivals/timeline?${params.toString()}`);
  },
  getTimelineEnvelope: ({ from, to, qualityBand = 'computed', category, region, search, lang = 'en' } = {}) => {
    const params = new URLSearchParams({ from, to, quality_band: qualityBand, lang });
    if (category) params.set('category', category);
    if (region) params.set('region', region);
    if (search) params.set('search', search);
    return fetchAPIEnvelope(`/festivals/timeline?${params.toString()}`);
  },
  getById: (id, year) => {
    const query = year ? `?year=${year}` : '';
    return fetchAPI(`/festivals/${id}${query}`);
  },
  getByIdEnvelope: (id, year) => {
    const query = year ? `?year=${year}` : '';
    return fetchAPIEnvelope(`/festivals/${id}${query}`);
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
  getToday: () => fetchAPI('/calendar/today'),
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
    fetchAPIEnvelope('/personal/panchanga', createPrivateJsonOptions({ date, lat, lon, tz })),
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
    fetchAPIEnvelope('/muhurta/heatmap', createPrivateJsonOptions({
      date,
      lat,
      lon,
      tz,
      type,
      assumption_set: assumptionSet,
    })),
};

export const kundaliAPI = {
  getKundali: ({ datetime, lat, lon, tz } = {}) =>
    fetchAPI('/kundali', createPrivateJsonOptions({ datetime, lat, lon, tz })),
  getLagna: ({ datetime, lat, lon, tz } = {}) =>
    fetchAPI('/kundali/lagna', createPrivateJsonOptions({ datetime, lat, lon, tz })),
  getGraph: ({ datetime, lat, lon, tz } = {}) =>
    fetchAPI('/kundali/graph', createPrivateJsonOptions({ datetime, lat, lon, tz })),
  getGraphEnvelope: ({ datetime, lat, lon, tz } = {}) =>
    fetchAPIEnvelope('/kundali/graph', createPrivateJsonOptions({ datetime, lat, lon, tz })),
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
