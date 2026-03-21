import {
  formatProductDate,
  formatProductTime,
  formatProductTimeRange,
} from '../utils/productDateTime';

describe('productDateTime', () => {
  it('formats date-only values against the selected product timezone', () => {
    expect(
      formatProductDate(
        '2026-03-20',
        { year: 'numeric', month: 'long', day: 'numeric' },
        { language: 'en', timeZone: 'America/New_York' },
      ),
    ).toContain('March');
  });

  it('formats times with the selected UI locale', () => {
    const formatted = formatProductTime('2026-03-20T10:30:00+05:45', {
      language: 'ne',
      timeZone: 'Asia/Kathmandu',
    });

    expect(formatted).not.toBe('');
  });

  it('builds a time range from the same product context', () => {
    expect(
      formatProductTimeRange(
        '2026-03-20T10:30:00+05:45',
        '2026-03-20T12:15:00+05:45',
        { language: 'en', timeZone: 'Asia/Kathmandu' },
      ),
    ).toMatch(/10:30|10\.30/i);
  });
});
