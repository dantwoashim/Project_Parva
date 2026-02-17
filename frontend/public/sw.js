/**
 * Project Parva Service Worker
 * Enables offline-first caching for the PWA experience.
 * 
 * Strategy:
 *   - Static assets: Cache-first (HTML, CSS, JS, fonts)
 *   - API: Network-first with cache fallback (panchanga, festivals)
 *   - Images: Cache-first with network fallback
 */

const CACHE_NAME = 'parva-v4-cache';
const STATIC_CACHE = 'parva-v4-static';
const API_CACHE = 'parva-v4-api';

const PRECACHE_URLS = [
    '/',
    '/index.html',
    '/manifest.json',
];

// Cache static assets during install
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// Clean old caches during activate
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) =>
            Promise.all(
                cacheNames.filter((name) => !name.startsWith('parva-v4')).map((name) => caches.delete(name))
            )
        ).then(() => self.clients.claim())
    );
});

// Fetch strategy
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') return;

    // Only intercept same-origin API requests.
    // Cross-origin local backend calls (e.g. localhost:8000) should fail transparently
    // so development errors are visible instead of converted to SW fallback 503 responses.
    if (url.origin === self.location.origin && url.pathname.startsWith('/v') && url.pathname.includes('/api/')) {
        event.respondWith(networkFirstWithCache(request, API_CACHE));
        return;
    }

    // Static assets: cache-first
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
    } catch (error) {
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
    } catch (error) {
        return new Response('Offline', { status: 503 });
    }
}
