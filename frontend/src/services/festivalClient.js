import {
  normalizeFestivalDetailEnvelope,
  normalizeFestivalTimelineEnvelope,
} from './apiContracts';
import { fetchAPI, fetchAPIEnvelope } from './apiCore';

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
  getById: (id, year, authorityMode) => {
    const params = new URLSearchParams();
    if (year) params.set('year', year);
    if (authorityMode) params.set('authority_mode', authorityMode);
    const query = params.toString();
    return fetchAPI(`/festivals/${id}${query ? `?${query}` : ''}`);
  },
  getByIdEnvelope: (id, year, authorityMode) => {
    const params = new URLSearchParams();
    if (year) params.set('year', year);
    if (authorityMode) params.set('authority_mode', authorityMode);
    const query = params.toString();
    return fetchAPIEnvelope(`/festivals/${id}${query ? `?${query}` : ''}`, { preferEnvelope: true }).then(normalizeFestivalDetailEnvelope);
  },
  getExplain: (id, year, authorityMode) => {
    const params = new URLSearchParams();
    if (year) params.set('year', year);
    if (authorityMode) params.set('authority_mode', authorityMode);
    const query = params.toString();
    return fetchAPI(`/festivals/${id}/explain${query ? `?${query}` : ''}`);
  },
  getDisputeAtlas: (year, limit = 18) => fetchAPI(`/festivals/disputes?year=${year}&limit=${limit}`),
  getProofCapsule: (id, year, authorityMode = 'authority_compare', riskMode = 'strict') => {
    const params = new URLSearchParams({ year, authority_mode: authorityMode, risk_mode: riskMode });
    return fetchAPI(`/festivals/${id}/proof-capsule?${params.toString()}`);
  },
  getTrace: (traceId) => fetchAPI(`/explain/${traceId}`),
  getDates: (id, years = 3) => fetchAPI(`/festivals/${id}/dates?years=${years}`),
  getOnDate: (date) => fetchAPI(`/festivals/on-date/${date}`),
};
