import '@testing-library/jest-dom/vitest';
import { cleanup, configure } from '@testing-library/react';
import { afterEach } from 'vitest';

configure({
  asyncUtilTimeout: 5000,
});

function queryMatchesWidth(query, width) {
  const minMatch = query.match(/min-width:\s*(\d+)px/);
  const maxMatch = query.match(/max-width:\s*(\d+)px/);
  const minWidth = minMatch ? Number(minMatch[1]) : null;
  const maxWidth = maxMatch ? Number(maxMatch[1]) : null;

  if (minWidth !== null && width < minWidth) return false;
  if (maxWidth !== null && width > maxWidth) return false;
  return true;
}

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query) => ({
    matches: queryMatchesWidth(query, window.innerWidth || 1024),
    media: query,
    onchange: null,
    addEventListener: () => {},
    removeEventListener: () => {},
    addListener: () => {},
    removeListener: () => {},
    dispatchEvent: () => false,
  }),
});

function resetStorage(storage) {
  if (!storage) {
    return;
  }
  if (typeof storage.clear === 'function') {
    storage.clear();
    return;
  }
  for (const key of Object.keys(storage)) {
    delete storage[key];
  }
}

afterEach(() => {
  cleanup();
  window.innerWidth = 1024;
  window.innerHeight = 768;
  resetStorage(window.localStorage);
  resetStorage(window.sessionStorage);
});
