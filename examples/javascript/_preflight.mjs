import { access } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

export const DEFAULT_EXAMPLE_API_BASE = 'https://api.prabinghimire1.com.np/v3/api';

const sdkDistUrl = new URL('../../packages/parva-js/dist/index.js', import.meta.url);

export function resolveApiBase() {
  const baseUrl = (process.env.PARVA_API_BASE || DEFAULT_EXAMPLE_API_BASE).replace(/\/+$/, '');
  console.error(`[parva-example] Using API base: ${baseUrl}`);
  return baseUrl;
}

export async function loadParvaClient() {
  try {
    await access(fileURLToPath(sdkDistUrl));
  } catch {
    console.error(
      '[parva-example] Missing packages/parva-js/dist/index.js. '
        + 'Run `npm test` from the repository root or `npm --prefix packages/parva-js test` before running JavaScript examples.',
    );
    process.exit(1);
  }
  return import(sdkDistUrl.href);
}

