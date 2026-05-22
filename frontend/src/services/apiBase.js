import { DEFAULT_PUBLIC_API_BASE } from '../config/publicEndpoints.js';

function trimSlash(value) {
  return String(value || '').trim().replace(/\/+$/, '');
}

export function resolveApiBase(env = import.meta.env) {
  const explicitBase = trimSlash(env?.VITE_API_BASE);
  if (explicitBase) {
    return explicitBase;
  }

  return DEFAULT_PUBLIC_API_BASE;
}

export const API_BASE = resolveApiBase();

export function apiUrl(path) {
  if (!path) return API_BASE;
  if (/^https?:\/\//i.test(path) || path.startsWith('webcal://')) {
    return path;
  }
  const normalizedPath = String(path).startsWith('/') ? String(path) : `/${path}`;
  return `${API_BASE}${normalizedPath}`;
}

export const apiHref = apiUrl;
