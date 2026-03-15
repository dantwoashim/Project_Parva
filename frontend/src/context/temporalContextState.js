export const STORAGE_KEY = 'parva.temporal_context.v2';
export const DEFAULT_LOCATION = { latitude: 27.7172, longitude: 85.324 };

function formatDateParts(date, timeZone) {
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
  const parts = formatter.formatToParts(date);
  const byType = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${byType.year}-${byType.month}-${byType.day}`;
}

export function todayIso(timeZone = 'Asia/Kathmandu') {
  const now = new Date(Date.now());
  try {
    return formatDateParts(now, timeZone || 'Asia/Kathmandu');
  } catch {
    return formatDateParts(now, 'Asia/Kathmandu');
  }
}

export function createInitialState() {
  const timezone = 'Asia/Kathmandu';
  return {
    date: todayIso(timezone),
    location: { ...DEFAULT_LOCATION },
    timezone,
    language: 'en',
    theme: 'nocturne-ink',
    lastViewed: '/',
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
    case 'hydrate': {
      const { mode: _legacyMode, qualityBand: _legacyQualityBand, ...rest } = action.payload || {};
      return {
        ...state,
        ...rest,
        location: {
          ...state.location,
          ...(action.payload?.location || {}),
        },
      };
    }
    case 'setDate':
      return { ...state, date: action.payload };
    case 'setLocation':
      return { ...state, location: { ...state.location, ...(action.payload || {}) } };
    case 'setTimezone':
      return { ...state, timezone: action.payload || 'Asia/Kathmandu' };
    case 'setLanguage':
      return { ...state, language: action.payload === 'ne' ? 'ne' : 'en' };
    case 'setTheme':
      return state.theme === (action.payload === 'nocturne-ink' ? 'nocturne-ink' : 'dawn-paper')
        ? state
        : { ...state, theme: action.payload === 'nocturne-ink' ? 'nocturne-ink' : 'dawn-paper' };
    case 'setLastViewed':
      return state.lastViewed === (action.payload || '/')
        ? state
        : { ...state, lastViewed: action.payload || '/' };
    default:
      return state;
  }
}
