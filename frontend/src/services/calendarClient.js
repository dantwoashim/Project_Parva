import {
  normalizeCalendarTodayPayload,
  normalizeTemporalCompassEnvelope,
} from './apiContracts';
import {
  createPrivateJsonOptions,
  fetchAPI,
  fetchAPIEnvelope,
} from './apiCore';
import { todayIso } from '../context/temporalContextState';

function normalizeCalendarDate(date) {
  if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date.trim())) {
    return date.trim();
  }
  return todayIso('Asia/Kathmandu');
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
  getCompassProofCapsule: ({ date, lat, lon, tz, qualityBand = 'computed', riskMode = 'strict' } = {}) =>
    fetchAPI('/temporal/compass/proof-capsule', createPrivateJsonOptions({
      date,
      lat,
      lon,
      tz,
      quality_band: qualityBand,
      risk_mode: riskMode,
    })),
};

export const glossaryAPI = {
  get: ({ domain, lang = 'en' } = {}) => fetchAPI(`/glossary?domain=${domain}&lang=${lang}`),
};

export const calendarAPI = {
  getMonth: (year, month) => fetchAPI(`/festivals/calendar/${year}/${month}`),
  getDualMonth: (year, month) => fetchAPI(`/calendar/dual-month?year=${year}&month=${month}`),
  getToday: async (riskMode) => {
    const query = riskMode ? `?risk_mode=${encodeURIComponent(riskMode)}` : '';
    return normalizeCalendarTodayPayload(await fetchAPI(`/calendar/today${query}`));
  },
  getTodayProofCapsule: (riskMode = 'strict') =>
    fetchAPI(`/calendar/today/proof-capsule?risk_mode=${encodeURIComponent(riskMode)}`),
  convertGregorian: (date) => fetchAPI(`/calendar/convert?date=${encodeURIComponent(date)}`),
  compareGregorian: (date) => fetchAPI(`/calendar/convert/compare?date=${encodeURIComponent(date)}`),
  convertBsToGregorian: ({ year, month, day }) => fetchAPI('/calendar/bs-to-gregorian', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ year, month, day }),
  }),
  getPanchanga: (date, riskMode) => {
    const params = new URLSearchParams({ date: normalizeCalendarDate(date) });
    if (riskMode) params.set('risk_mode', riskMode);
    return fetchAPI(`/calendar/panchanga?${params.toString()}`);
  },
  getPanchangaEnvelope: (date, riskMode) => {
    const params = new URLSearchParams({ date: normalizeCalendarDate(date) });
    if (riskMode) params.set('risk_mode', riskMode);
    return fetchAPIEnvelope(`/calendar/panchanga?${params.toString()}`);
  },
  getPanchangaProofCapsule: (date, riskMode = 'strict') => {
    const params = new URLSearchParams({ date: normalizeCalendarDate(date), risk_mode: riskMode });
    return fetchAPI(`/calendar/panchanga/proof-capsule?${params.toString()}`);
  },
  getTithi: (date, latitude, longitude, riskMode) => {
    const params = new URLSearchParams({ date });
    if (latitude !== undefined) params.set('latitude', latitude);
    if (longitude !== undefined) params.set('longitude', longitude);
    if (riskMode) params.set('risk_mode', riskMode);
    return fetchAPI(`/calendar/tithi?${params.toString()}`);
  },
  getTithiProofCapsule: (date, latitude, longitude, riskMode = 'strict') => {
    const params = new URLSearchParams({ date, risk_mode: riskMode });
    if (latitude !== undefined) params.set('latitude', latitude);
    if (longitude !== undefined) params.set('longitude', longitude);
    return fetchAPI(`/calendar/tithi/proof-capsule?${params.toString()}`);
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
