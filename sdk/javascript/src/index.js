/**
 * Parva JavaScript SDK
 * ====================
 *
 * Client library for the Parva API — Nepal's temporal infrastructure.
 *
 * Usage:
 *   import { ParvaClient } from './parva';
 *   const client = new ParvaClient('https://parva.example.com');
 *   const today = await client.today();
 */

class ParvaClient {
    /**
     * @param {string} baseUrl - Parva API base URL
     * @param {Object} options - Additional options
     * @param {number} options.timeout - Request timeout in ms (default: 30000)
     */
    constructor(baseUrl = 'http://localhost:8000', options = {}) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.timeout = options.timeout || 30000;
    }

    async _get(path, params = {}) {
        const url = new URL(`${this.baseUrl}${path}`);
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                url.searchParams.append(key, value);
            }
        });

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url.toString(), {
                headers: { 'Accept': 'application/json' },
                signal: controller.signal,
            });

            if (!response.ok) {
                const body = await response.text();
                let detail;
                try {
                    detail = JSON.parse(body).detail || body;
                } catch {
                    detail = body;
                }
                throw new ParvaError(response.status, detail);
            }

            return response.json();
        } finally {
            clearTimeout(timeoutId);
        }
    }

    async _getRaw(path, params = {}) {
        const url = new URL(`${this.baseUrl}${path}`);
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined) url.searchParams.append(key, value);
        });
        const response = await fetch(url.toString());
        return response.text();
    }

    // ── Core Calendar ─────────────────────────────────────────
    async convert(date) { return this._get('/api/calendar/convert', { date }); }
    async today() { return this._get('/api/calendar/today'); }
    async panchanga(date) { return this._get('/api/calendar/panchanga', { date }); }
    async panchangaRange(start, days = 7) { return this._get('/api/calendar/panchanga/range', { start, days }); }

    // ── Festivals ─────────────────────────────────────────────
    async calculateFestival(festivalId, year) { return this._get(`/api/calendar/festivals/calculate/${festivalId}`, { year }); }
    async upcomingFestivals(days = 30) { return this._get('/api/calendar/festivals/upcoming', { days }); }

    // ── Cross-Calendar ────────────────────────────────────────
    async crossConvert(date, to) { return this._get('/api/calendar/cross/convert', { date, to }); }
    async convertAll(date) { return this._get('/api/calendar/cross/convert-all', { date }); }
    async calendars() { return this._get('/api/calendar/cross/calendars'); }

    // ── iCal ──────────────────────────────────────────────────
    async ical(year) { return this._getRaw('/api/calendar/ical', { year }); }

    // ── Engine ────────────────────────────────────────────────
    async health() { return this._get('/api/engine/health'); }
    async engineConfig() { return this._get('/api/engine/config'); }
}

class ParvaError extends Error {
    constructor(statusCode, detail) {
        super(`Parva API error ${statusCode}: ${detail}`);
        this.statusCode = statusCode;
        this.detail = detail;
    }
}

// CommonJS + ESM compatible export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ParvaClient, ParvaError };
}
export { ParvaClient, ParvaError };
