import { apiUrl, resolveApiBase } from '../services/apiBase';

describe('apiBase helpers', () => {
  it('resolves the configured API base without trailing slashes', () => {
    expect(resolveApiBase({ VITE_API_BASE: 'https://api.example.test/v3/api/' })).toBe(
      'https://api.example.test/v3/api',
    );
  });

  it('builds backend hrefs from the central API base', () => {
    expect(apiUrl('/calendar/today')).toBe(
      'https://api.prabinghimire1.com.np/v3/api/calendar/today',
    );
    expect(apiUrl('feeds/all.ics?years=1')).toBe(
      'https://api.prabinghimire1.com.np/v3/api/feeds/all.ics?years=1',
    );
  });

  it('keeps absolute URLs untouched', () => {
    expect(apiUrl('https://example.com/v3/api/calendar/today')).toBe(
      'https://example.com/v3/api/calendar/today',
    );
  });
});
