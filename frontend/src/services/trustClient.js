import { fetchAPI } from './apiCore';

export const reliabilityAPI = {
  getBenchmarkManifest: () => fetchAPI('/reliability/benchmark-manifest'),
  getSourceReviewQueue: () => fetchAPI('/reliability/source-review-queue'),
  getBoundarySuite: () => fetchAPI('/reliability/boundary-suite'),
  getDifferentialManifest: () => fetchAPI('/reliability/differential-manifest'),
};
