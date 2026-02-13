/**
 * API Service
 * ===========
 *
 * Handles all API calls to the Parva backend.
 *
 * Notes:
 * - Defaults to v5 API (authority envelope).
 * - Falls back gracefully for v2/v3/v4 style payloads.
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/v5/api';

/**
 * Fetch wrapper with envelope-aware parsing and error handling.
 *
 * @param {string} endpoint
 * @param {Object} options
 * @param {"json"|"text"} parseAs
 * @returns {Promise<any>}
 */
export async function fetchAPI(endpoint, options = {}, parseAs = 'json') {
    const envelope = await fetchAPIEnvelope(endpoint, options, parseAs);
    if (parseAs === 'text') return envelope;
    return envelope.data;
}

/**
 * Fetch wrapper that preserves v4/v5 envelope metadata.
 *
 * @param {string} endpoint
 * @param {Object} options
 * @param {"json"|"text"} parseAs
 * @returns {Promise<any>}
 */
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
        const message = `API Error: ${response.status} ${response.statusText}`;
        throw new Error(message);
    }

    if (parseAs === 'text') {
        return response.text();
    }

    const payload = await response.json();
    // v4 contract uses { data, meta }. v2/v3 may return plain objects.
    if (payload && typeof payload === 'object' && 'data' in payload && 'meta' in payload) {
        return payload;
    }
    return {
        data: payload,
        meta: {
            confidence: { level: 'unknown', score: 0.5 },
            method: 'unknown',
            provenance: {},
            uncertainty: { boundary_risk: 'unknown', interval_hours: null },
            trace_id: null,
            policy: { profile: 'np-mainstream', jurisdiction: 'NP', advisory: true },
        },
    };
}

export function getApiBase() {
    return API_BASE;
}

// Festival APIs
export const festivalAPI = {
    getAll: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return fetchAPI(`/festivals${query ? `?${query}` : ''}`);
    },

    getUpcoming: (days = 90) => fetchAPI(`/festivals/upcoming?days=${days}`),

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

// Calendar APIs
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

// Feed/iCal APIs
export const feedAPI = {
    getAllLink: (years = 2, lang = 'en') =>
        `${API_BASE}/feeds/all.ics?years=${years}&lang=${lang}`,
    getNationalLink: (years = 2, lang = 'en') =>
        `${API_BASE}/feeds/national.ics?years=${years}&lang=${lang}`,
    getNewariLink: (years = 2, lang = 'en') =>
        `${API_BASE}/feeds/newari.ics?years=${years}&lang=${lang}`,
    getCustomLink: (festivalIds = [], years = 2, lang = 'en') => {
        const festivals = encodeURIComponent(festivalIds.join(','));
        return `${API_BASE}/feeds/custom.ics?festivals=${festivals}&years=${years}&lang=${lang}`;
    },
    getPreview: (days = 30, lang = 'en') => fetchAPI(`/feeds/next?days=${days}&lang=${lang}`),
};

export default {
    festivals: festivalAPI,
    calendar: calendarAPI,
    feeds: feedAPI,
};
