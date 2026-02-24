/**
 * API Service
 * ==========
 * Public profile defaults to v3.
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/v3/api';

export async function fetchAPI(endpoint, options = {}, parseAs = 'json') {
  const envelope = await fetchAPIEnvelope(endpoint, options, parseAs);
  if (parseAs === 'text') return envelope;
  return envelope.data;
}

export async function fetchAPIEnvelope(endpoint, options = {}, parseAs = 'json') {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      ...(parseAs === 'json' ? { 'Content-Type': 'application/json' } : {}),
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
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
  getCompass: ({ date, lat, lon, tz, qualityBand = 'computed' } = {}) => {
    const params = new URLSearchParams({ date, quality_band: qualityBand });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    return fetchAPI(`/temporal/compass?${params.toString()}`);
  },
  getCompassEnvelope: ({ date, lat, lon, tz, qualityBand = 'computed' } = {}) => {
    const params = new URLSearchParams({ date, quality_band: qualityBand });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    return fetchAPIEnvelope(`/temporal/compass?${params.toString()}`);
  },
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
  getTimeline: ({ from, to, qualityBand = 'computed', category, region, lang = 'en' } = {}) => {
    const params = new URLSearchParams({ from, to, quality_band: qualityBand, lang });
    if (category) params.set('category', category);
    if (region) params.set('region', region);
    return fetchAPI(`/festivals/timeline?${params.toString()}`);
  },
  getTimelineEnvelope: ({ from, to, qualityBand = 'computed', category, region, lang = 'en' } = {}) => {
    const params = new URLSearchParams({ from, to, quality_band: qualityBand, lang });
    if (category) params.set('category', category);
    if (region) params.set('region', region);
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
  getPanchanga: ({ date, lat, lon, tz } = {}) => {
    const params = new URLSearchParams({ date });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    return fetchAPI(`/personal/panchanga?${params.toString()}`);
  },
  getPanchangaEnvelope: ({ date, lat, lon, tz } = {}) => {
    const params = new URLSearchParams({ date });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    return fetchAPIEnvelope(`/personal/panchanga?${params.toString()}`);
  },
};

export const muhurtaAPI = {
  getDay: ({ date, lat, lon, tz, birthNakshatra } = {}) => {
    const params = new URLSearchParams({ date });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    if (birthNakshatra) params.set('birth_nakshatra', birthNakshatra);
    return fetchAPI(`/muhurta?${params.toString()}`);
  },
  getAuspicious: ({ date, type = 'general', lat, lon, tz, birthNakshatra, assumptionSet = 'np-mainstream-v2' } = {}) => {
    const params = new URLSearchParams({ date, type, assumption_set: assumptionSet });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    if (birthNakshatra) params.set('birth_nakshatra', birthNakshatra);
    return fetchAPI(`/muhurta/auspicious?${params.toString()}`);
  },
  getRahuKalam: ({ date, lat, lon, tz } = {}) => {
    const params = new URLSearchParams({ date });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    return fetchAPI(`/muhurta/rahu-kalam?${params.toString()}`);
  },
  getHeatmap: ({ date, lat, lon, tz, type = 'general', assumptionSet = 'np-mainstream-v2' } = {}) => {
    const params = new URLSearchParams({ date, type, assumption_set: assumptionSet });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    return fetchAPI(`/muhurta/heatmap?${params.toString()}`);
  },
  getHeatmapEnvelope: ({ date, lat, lon, tz, type = 'general', assumptionSet = 'np-mainstream-v2' } = {}) => {
    const params = new URLSearchParams({ date, type, assumption_set: assumptionSet });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    return fetchAPIEnvelope(`/muhurta/heatmap?${params.toString()}`);
  },
};

export const kundaliAPI = {
  getKundali: ({ datetime, lat, lon, tz } = {}) => {
    const params = new URLSearchParams({ datetime });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    return fetchAPI(`/kundali?${params.toString()}`);
  },
  getLagna: ({ datetime, lat, lon, tz } = {}) => {
    const params = new URLSearchParams({ datetime });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    return fetchAPI(`/kundali/lagna?${params.toString()}`);
  },
  getGraph: ({ datetime, lat, lon, tz } = {}) => {
    const params = new URLSearchParams({ datetime });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    return fetchAPI(`/kundali/graph?${params.toString()}`);
  },
  getGraphEnvelope: ({ datetime, lat, lon, tz } = {}) => {
    const params = new URLSearchParams({ datetime });
    if (lat !== undefined) params.set('lat', lat);
    if (lon !== undefined) params.set('lon', lon);
    if (tz) params.set('tz', tz);
    return fetchAPIEnvelope(`/kundali/graph?${params.toString()}`);
  },
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
