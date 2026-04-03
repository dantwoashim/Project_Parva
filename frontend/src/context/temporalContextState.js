export const STORAGE_KEY = 'parva.temporal_context.v2';
export const DEFAULT_LOCATION = { latitude: 27.7172, longitude: 85.324 };
const SUPPORTED_THEMES = new Set(['warm-paper', 'dawn-paper', 'ink-black']);
const SUPPORTED_LANGUAGES = new Set(['en', 'ne']);

function normalizeTheme(theme, fallback = 'warm-paper') {
  if (SUPPORTED_THEMES.has(theme)) return theme;
  return fallback;
}

function normalizeLanguage(language, fallback = 'en') {
  if (SUPPORTED_LANGUAGES.has(language)) return language;
  return fallback;
}

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
    theme: 'warm-paper',
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
    const hydrated = reducer(baseState, { type: 'hydrate', payload: parsed });
    return {
      ...hydrated,
      date: todayIso(hydrated.timezone || baseState.timezone),
    };
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
        language: normalizeLanguage(action.payload?.language, state.language),
        theme: normalizeTheme(action.payload?.theme, state.theme),
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
      return state.language === normalizeLanguage(action.payload, state.language)
        ? state
        : { ...state, language: normalizeLanguage(action.payload, state.language) };
    case 'setTheme':
      return state.theme === normalizeTheme(action.payload, state.theme)
        ? state
        : { ...state, theme: normalizeTheme(action.payload, state.theme) };
    case 'setLastViewed':
      return state.lastViewed === (action.payload || '/')
        ? state
        : { ...state, lastViewed: action.payload || '/' };
    default:
      return state;
  }
}
