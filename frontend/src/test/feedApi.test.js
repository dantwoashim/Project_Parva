import { createFeedAPI } from '../services/feedApi';

describe('createFeedAPI', () => {
  it('builds feed links and integration endpoints from the provided api base', async () => {
    const fetchAPI = vi.fn(async () => ({ ok: true }));
    const api = createFeedAPI({ apiBase: '/v3/api', fetchAPI });

    expect(api.getAllLink(2, 'en')).toBe('/v3/api/feeds/all.ics?years=2&lang=en');
    expect(api.getCustomLink(['dashain', 'tihar'], 3, 'ne')).toBe('/v3/api/feeds/custom.ics?festivals=dashain%2Ctihar&years=3&lang=ne');
    expect(api.getDownloadLink('/v3/api/feeds/all.ics?years=2&lang=en')).toContain('download=1');
    expect(api.getAppleSubscribeLink('https://example.com/v3/api/feeds/all.ics')).toBe('webcal://example.com/v3/api/feeds/all.ics');

    await api.getCatalog({ years: 4, startYear: 2082, lang: 'ne' });
    await api.getCustomPlan({ festivalIds: ['dashain'], years: 1, startYear: 2083, lang: 'en' });

    expect(fetchAPI).toHaveBeenNthCalledWith(1, '/feeds/integrations/catalog?years=4&lang=ne&start_year=2082');
    expect(fetchAPI).toHaveBeenNthCalledWith(2, '/feeds/integrations/custom-plan?festivals=dashain&years=1&lang=en&start_year=2083');
  });
});
