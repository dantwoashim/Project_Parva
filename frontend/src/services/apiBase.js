const DEFAULT_API_BASE = 'https://api.prabinghimire1.com.np/v3/api';

function trimSlash(value) {
  return String(value || '').trim().replace(/\/+$/, '');
}

export function resolveApiBase(env = import.meta.env) {
  const explicitBase = trimSlash(env?.VITE_API_BASE);
  if (explicitBase) {
    return explicitBase;
  }

  return DEFAULT_API_BASE;
}

export const API_BASE = resolveApiBase();
