/**
 * API Service
 * ==========
 * Public profile defaults to v3.
 */

export {
  ParvaApiError,
  ensureJsonPayload,
  fetchAPI,
  fetchAPIEnvelope,
  getApiBase,
} from './apiCore';
export { calendarAPI, glossaryAPI, temporalAPI } from './calendarClient';
export { festivalAPI } from './festivalClient';
export { feedAPI } from './integrationClient';
export { kundaliAPI, muhurtaAPI, personalAPI, placesAPI } from './personalClient';
export { reliabilityAPI } from './trustClient';

import { calendarAPI, glossaryAPI, temporalAPI } from './calendarClient';
import { festivalAPI } from './festivalClient';
import { feedAPI } from './integrationClient';
import { kundaliAPI, muhurtaAPI, personalAPI, placesAPI } from './personalClient';
import { reliabilityAPI } from './trustClient';

export default {
  temporal: temporalAPI,
  glossary: glossaryAPI,
  festivals: festivalAPI,
  reliability: reliabilityAPI,
  calendar: calendarAPI,
  personal: personalAPI,
  muhurta: muhurtaAPI,
  kundali: kundaliAPI,
  places: placesAPI,
  feeds: feedAPI,
};
