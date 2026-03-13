import '@testing-library/jest-dom/vitest';
import { cleanup, configure } from '@testing-library/react';
import { afterEach } from 'vitest';

configure({
  asyncUtilTimeout: 5000,
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
  resetStorage(window.localStorage);
  resetStorage(window.sessionStorage);
});
