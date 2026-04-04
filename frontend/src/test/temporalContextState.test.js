import {
  STORAGE_KEY,
  createInitialState,
  loadInitialState,
  reducer,
  todayIso,
} from '../context/temporalContextState';

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
      theme: 'warm-paper',
    });
  });

  it('hydrates timezone and location but resets the stored date back to today on refresh', () => {
    vi.setSystemTime(new Date('2026-02-15T02:30:00.000Z'));
    const memoryStorage = {
      getItem: vi.fn(() => JSON.stringify({
        date: '2026-01-01',
        timezone: 'America/New_York',
        location: { latitude: 40.7128, longitude: -74.006 },
      })),
    };
    Object.defineProperty(window, 'localStorage', {
      value: memoryStorage,
      configurable: true,
    });

    const state = loadInitialState();

    expect(memoryStorage.getItem).toHaveBeenCalledWith(STORAGE_KEY);
    expect(state.timezone).toBe('America/New_York');
    expect(state.location).toMatchObject({ latitude: 40.7128, longitude: -74.006 });
    expect(state.date).toBe('2026-02-14');
  });

  it('preserves dawn-paper as a distinct theme', () => {
    const state = reducer(createInitialState(), { type: 'setTheme', payload: 'dawn-paper' });
    expect(state.theme).toBe('dawn-paper');
  });

  it('allows supported language changes instead of forcing english', () => {
    const state = reducer(createInitialState(), { type: 'setLanguage', payload: 'ne' });
    expect(state.language).toBe('ne');
  });
});
