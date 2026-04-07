import {
  normalizeKundaliGraphEnvelope,
  normalizeMuhurtaCalendarPayload,
  normalizeMuhurtaHeatmapEnvelope,
  normalizePersonalContextEnvelope,
  normalizePersonalPanchangaEnvelope,
  normalizePlaceSearchPayload,
} from './apiContracts';
import {
  createPrivateJsonOptions,
  fetchAPI,
  fetchAPIEnvelope,
  normalizeCoordinateField,
} from './apiCore';

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
  getPanchangaProofCapsule: ({ date, lat, lon, tz, riskMode = 'strict' } = {}) =>
    fetchAPI('/personal/panchanga/proof-capsule', createPrivateJsonOptions({
      date,
      lat,
      lon,
      tz,
      risk_mode: riskMode,
    })),
  getContextProofCapsule: ({ date, lat, lon, tz, riskMode = 'strict' } = {}) =>
    fetchAPI('/personal/context/proof-capsule', createPrivateJsonOptions({
      date,
      lat,
      lon,
      tz,
      risk_mode: riskMode,
    })),
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
  getCalendar: ({ from, to, lat, lon, tz, type = 'general', assumptionSet = 'np-mainstream-v2' } = {}) => {
    const params = new URLSearchParams({
      from,
      to,
      type,
      assumption_set: assumptionSet,
    });
    if (lat != null) params.set('lat', normalizeCoordinateField(lat));
    if (lon != null) params.set('lon', normalizeCoordinateField(lon));
    if (tz) params.set('tz', tz);
    return fetchAPI(`/muhurta/calendar?${params.toString()}`).then(normalizeMuhurtaCalendarPayload);
  },
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

export const placesAPI = {
  search: ({ query, limit = 5 } = {}) => {
    const params = new URLSearchParams({ q: query || '', limit: String(limit) });
    return fetchAPI(`/places/search?${params.toString()}`).then(normalizePlaceSearchPayload);
  },
};
