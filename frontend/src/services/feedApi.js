function toAbsoluteApiUrl(value) {
  if (!value) return '';
  try {
    return new URL(value, window.location.origin).toString();
  } catch {
    return value;
  }
}

function toWebcalUrl(value) {
  const absolute = toAbsoluteApiUrl(value);
  if (absolute.startsWith('https://')) return `webcal://${absolute.slice('https://'.length)}`;
  if (absolute.startsWith('http://')) return `webcal://${absolute.slice('http://'.length)}`;
  return absolute;
}

function appendQueryParam(url, key, value) {
  const absolute = toAbsoluteApiUrl(url);
  const next = new URL(absolute);
  next.searchParams.set(key, value);
  return next.toString();
}

export function createFeedAPI({ apiBase, fetchAPI }) {
  return {
    getAllLink: (years = 2, lang = 'en') => `${apiBase}/feeds/all.ics?years=${years}&lang=${lang}`,
    getNationalLink: (years = 2, lang = 'en') => `${apiBase}/feeds/national.ics?years=${years}&lang=${lang}`,
    getNewariLink: (years = 2, lang = 'en') => `${apiBase}/feeds/newari.ics?years=${years}&lang=${lang}`,
    getCustomLink: (festivalIds = [], years = 2, lang = 'en') => {
      const festivals = encodeURIComponent(festivalIds.join(','));
      return `${apiBase}/feeds/custom.ics?festivals=${festivals}&years=${years}&lang=${lang}`;
    },
    getDownloadLink: (url) => appendQueryParam(url, 'download', '1'),
    getAppleSubscribeLink: (url) => toWebcalUrl(url),
    getGoogleSetupUrl: () => 'https://calendar.google.com/calendar/u/0/r/settings/addbyurl',
    getCatalog: ({ years = 2, startYear, lang = 'en' } = {}) => {
      const params = new URLSearchParams({ years: String(years), lang });
      if (startYear) params.set('start_year', String(startYear));
      return fetchAPI(`/feeds/integrations/catalog?${params.toString()}`);
    },
    getCustomPlan: ({ festivalIds = [], years = 2, startYear, lang = 'en' } = {}) => {
      const params = new URLSearchParams({
        festivals: festivalIds.join(','),
        years: String(years),
        lang,
      });
      if (startYear) params.set('start_year', String(startYear));
      return fetchAPI(`/feeds/integrations/custom-plan?${params.toString()}`);
    },
    getPreview: (days = 30, lang = 'en') => fetchAPI(`/feeds/next?days=${days}&lang=${lang}`),
  };
}
