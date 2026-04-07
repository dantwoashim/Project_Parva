import { createFeedAPI } from './feedApi';
import { fetchAPI, getApiBase } from './apiCore';

export const feedAPI = createFeedAPI({
  apiBase: getApiBase(),
  fetchAPI,
});
