import '@testing-library/jest-dom/vitest';
import { cleanup, configure } from '@testing-library/react';
import { afterEach, beforeEach } from 'vitest';

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

function createMemoryStorage() {
  const store = new Map();
  return {
    get length() {
      return store.size;
    },
    clear: () => store.clear(),
    getItem: (key) => (store.has(String(key)) ? store.get(String(key)) : null),
    key: (index) => Array.from(store.keys())[index] ?? null,
    removeItem: (key) => store.delete(String(key)),
    setItem: (key, value) => store.set(String(key), String(value)),
  };
}

function ensureStorage(name) {
  const descriptor = Object.getOwnPropertyDescriptor(window, name);
  const storage = descriptor && Object.prototype.hasOwnProperty.call(descriptor, 'value')
    ? descriptor.value
    : null;
  if (
    storage
    && typeof storage.clear === 'function'
    && typeof storage.getItem === 'function'
    && typeof storage.setItem === 'function'
    && typeof storage.removeItem === 'function'
  ) {
    return;
  }
  Object.defineProperty(window, name, {
    configurable: true,
    value: createMemoryStorage(),
  });
}

beforeEach(() => {
  ensureStorage('localStorage');
  ensureStorage('sessionStorage');
});

afterEach(() => {
  cleanup();
  window.innerWidth = 1024;
  window.innerHeight = 768;
  resetStorage(window.localStorage);
  resetStorage(window.sessionStorage);
  ensureStorage('localStorage');
  ensureStorage('sessionStorage');
});
