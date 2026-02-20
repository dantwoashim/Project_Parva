/**
 * Project Parva Service Worker
 *
 * Strategy:
 * - Same-origin static assets: cache-first.
 * - Same-origin API requests: network-first with cache fallback.
 * - Cross-origin requests: bypass (never intercept).
 */

const STATIC_CACHE = 'parva-v5-static';
const API_CACHE = 'parva-v5-api';
const CACHE_PREFIX = 'parva-v5';

const PRECACHE_URLS = ['/', '/index.html', '/manifest.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => Promise.all(
      cacheNames
        .filter((name) => !name.startsWith(CACHE_PREFIX))
        .map((name) => caches.delete(name))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) {
    // Never intercept cross-origin API calls (important in local dev).
    return;
  }

  if (url.pathname.startsWith('/v') && url.pathname.includes('/api/')) {
    event.respondWith(networkFirstWithCache(request, API_CACHE));
    return;
  }

  event.respondWith(cacheFirstWithNetwork(request, STATIC_CACHE));
});

async function networkFirstWithCache(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response(
      JSON.stringify({ error: 'offline', message: 'No cached data available' }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

async function cacheFirstWithNetwork(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Offline', { status: 503 });
  }
}
