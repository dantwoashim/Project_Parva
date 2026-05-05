/**
 * Parva update-safe service worker.
 *
 * Do not cache the SPA shell. The app must show the newest deployment on a
 * normal reload, not only after a hard refresh.
 */

const CACHE_PREFIXES = ['parva-v'];

self.addEventListener('install', (event) => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => Promise.all(
        cacheNames
          .filter((name) => CACHE_PREFIXES.some((prefix) => name.startsWith(prefix)))
          .map((name) => caches.delete(name)),
      ))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate' || url.pathname === '/' || url.pathname.endsWith('/index.html')) {
    event.respondWith(fetchFresh(request));
    return;
  }

  if (url.pathname === '/sw.js' || url.pathname === '/manifest.json') {
    event.respondWith(fetchFresh(request));
    return;
  }

  if (url.pathname.startsWith('/v') && url.pathname.includes('/api/')) {
    event.respondWith(fetchFresh(request));
  }
});

async function fetchFresh(request) {
  try {
    return await fetch(request, { cache: 'no-store' });
  } catch {
    return new Response('Offline', {
      status: 503,
      headers: { 'Cache-Control': 'no-store' },
    });
  }
}
