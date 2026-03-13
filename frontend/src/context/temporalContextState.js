export const STORAGE_KEY = 'parva.temporal_context.v2';
export const DEFAULT_LOCATION = { latitude: 27.7172, longitude: 85.324 };

export function todayIso() {
  return new Date(Date.now()).toISOString().slice(0, 10);
}

export function createInitialState() {
  return {
    date: todayIso(),
    location: { ...DEFAULT_LOCATION },
    timezone: 'Asia/Kathmandu',
    mode: 'observance',
    language: 'en',
    qualityBand: 'computed',
  };
}

export function loadInitialState() {
  const baseState = createInitialState();

  if (
    typeof localStorage === 'undefined'
    || typeof localStorage.getItem !== 'function'
  ) {
    return baseState;
  }

  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return baseState;
    const parsed = JSON.parse(raw);
    return reducer(baseState, { type: 'hydrate', payload: parsed });
  } catch {
    return baseState;
  }
}

export function reducer(state, action) {
  switch (action.type) {
    case 'hydrate':
      return {
        ...state,
        ...(action.payload || {}),
        location: {
          ...state.location,
          ...(action.payload?.location || {}),
        },
      };
    case 'setDate':
      return { ...state, date: action.payload };
    case 'setLocation':
      return { ...state, location: { ...state.location, ...(action.payload || {}) } };
    case 'setTimezone':
      return { ...state, timezone: action.payload || 'Asia/Kathmandu' };
    case 'setMode':
      return { ...state, mode: action.payload === 'authority' ? 'authority' : 'observance' };
    case 'setLanguage':
      return { ...state, language: action.payload === 'ne' ? 'ne' : 'en' };
    case 'setQualityBand':
      return { ...state, qualityBand: action.payload || 'computed' };
    default:
      return state;
  }
}
