import { createInitialState, todayIso } from '../context/temporalContextState';

describe('temporal context state', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('defaults todayIso to Asia/Kathmandu', () => {
    vi.setSystemTime(new Date('2026-02-14T20:30:00.000Z'));

    expect(todayIso()).toBe('2026-02-15');
  });

  it('supports an explicit non-Nepal timezone', () => {
    vi.setSystemTime(new Date('2026-02-15T02:30:00.000Z'));

    expect(todayIso('America/New_York')).toBe('2026-02-14');
  });

  it('creates initial state using the Kathmandu default timezone', () => {
    vi.setSystemTime(new Date('2026-02-14T20:30:00.000Z'));

    expect(createInitialState()).toMatchObject({
      date: '2026-02-15',
      timezone: 'Asia/Kathmandu',
      location: { latitude: 27.7172, longitude: 85.324 },
      language: 'en',
      theme: 'nocturne-ink',
    });
  });
});
