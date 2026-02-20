import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

function jsonResponse(payload) {
  return {
    ok: true,
    status: 200,
    statusText: 'OK',
    json: async () => payload,
    text: async () => JSON.stringify(payload),
  };
}

function buildFetchMock() {
  return vi.fn(async (input) => {
    const url = String(input);

    if (url.includes('/festivals') && !url.includes('/festivals/')) {
      return jsonResponse({
        data: {
          festivals: [
            {
              id: 'dashain',
              name: 'Dashain',
              category: 'national',
              duration_days: 10,
              next_occurrence: '2026-10-20',
            },
          ],
          total: 1,
        },
        meta: {},
      });
    }

    if (url.includes('/festivals/coverage/scoreboard')) {
      return jsonResponse({
        data: {
          computed: { count: 323, pct: 71.3 },
          provisional: { count: 111, pct: 24.5 },
          inventory: { count: 19, pct: 4.2 },
          claim_guard: { headline_metric: 'computed', safe_to_claim_300: true },
        },
        meta: {},
      });
    }

    if (url.includes('/calendar/panchanga')) {
      return jsonResponse({
        data: {
          date: '2026-02-12',
          bikram_sambat: { year: 2082, month: 10, day: 30, month_name: 'Magh' },
          panchanga: {
            confidence: 'astronomical',
            tithi: { number: 10, name: 'Dashami', paksha: 'shukla', method: 'ephemeris_udaya', sunrise_used: '2026-02-12T06:45:00+05:45' },
            nakshatra: { name: 'Rohini', pada: 2 },
            yoga: { name: 'Siddha', number: 1 },
            karana: { name: 'Bava', number: 1 },
            vaara: { name_english: 'Thursday', name_sanskrit: 'Guruvara' },
          },
          ephemeris: { mode: 'swiss_moshier' },
        },
        meta: {},
      });
    }

    if (url.includes('/resolve?')) {
      return jsonResponse({ data: { trace: { trace_id: 'tr_routes', explain: 'routes test fixture' } }, meta: {} });
    }

    if (url.includes('/personal/panchanga')) {
      return jsonResponse({
        data: {
          date: '2026-02-12',
          bikram_sambat: { year: 2082, month: 10, day: 30, month_name: 'Magh' },
          tithi: { number: 10, name: 'Dashami', paksha: 'shukla' },
          nakshatra: { number: 4, name: 'Rohini' },
          yoga: { number: 1, name: 'Siddha' },
          karana: { number: 1, name: 'Bava' },
          vaara: { name_english: 'Thursday', name_sanskrit: 'Guruvara' },
          location: { latitude: 27.7172, longitude: 85.3240, timezone: 'Asia/Kathmandu' },
          method_profile: 'personal_panchanga_v2_udaya',
          quality_band: 'gold',
          advisory_scope: 'ritual_planning',
          calculation_trace_id: 'tr_personal_routes_001',
        },
        meta: {},
      });
    }

    if (url.includes('/muhurta/auspicious')) {
      return jsonResponse({
        data: {
          method_profile: 'muhurta_v2_hora_chaughadia_tarabala',
          best_window: { name: 'Abhijit Muhurta', start: '11:48', end: '12:36', score: 88 },
          ranked_muhurtas: [{ score: 88 }, { score: 75 }],
          muhurtas: [{ index: 1, number: 7, name: 'Abhijit Muhurta', start: '11:48', end: '12:36', score: 88 }],
          tara_bala: { quality: 'good' },
        },
        meta: {},
      });
    }

    if (url.includes('/muhurta/rahu-kalam')) {
      return jsonResponse({ data: { weekday: 'Thursday', rahu_kalam: { segment: 7, start: '13:36', end: '15:00' } }, meta: {} });
    }

    if (url.includes('/muhurta?')) {
      return jsonResponse({
        data: {
          muhurtas: Array.from({ length: 30 }).map((_, index) => ({ number: index + 1, duration_minutes: 48, name: `Muhurta ${index + 1}` })),
          day_muhurtas: Array.from({ length: 15 }).map((_, index) => ({ number: index + 1 })),
          night_muhurtas: Array.from({ length: 15 }).map((_, index) => ({ number: index + 16 })),
          hora: {
            day: Array.from({ length: 12 }).map((_, index) => ({ number: index + 1, lord_display: 'Sun' })),
            night: Array.from({ length: 12 }).map((_, index) => ({ number: index + 1, lord_display: 'Moon' })),
          },
          chaughadia: {
            day: Array.from({ length: 8 }).map((_, index) => ({ number: index + 1, name_display: 'Labh' })),
            night: Array.from({ length: 8 }).map((_, index) => ({ number: index + 1, name_display: 'Amrit' })),
          },
          method_profile: 'muhurta_v2_hora_chaughadia_tarabala',
        },
        meta: {},
      });
    }

    if (url.includes('/kundali?')) {
      return jsonResponse({
        data: {
          lagna: { rashi_english: 'Pisces', rashi_sanskrit: 'Meena', longitude: 12.3 },
          grahas: {
            sun: { name_sanskrit: 'Surya', name_english: 'Sun', rashi_english: 'Aquarius', longitude: 332, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            moon: { name_sanskrit: 'Chandra', name_english: 'Moon', rashi_english: 'Capricorn', longitude: 288, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            mars: { name_sanskrit: 'Mangala', name_english: 'Mars', rashi_english: 'Cancer', longitude: 102, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            mercury: { name_sanskrit: 'Budha', name_english: 'Mercury', rashi_english: 'Aquarius', longitude: 325, is_retrograde: false, dignity: { state: 'own', strength: 'strong' } },
            jupiter: { name_sanskrit: 'Guru', name_english: 'Jupiter', rashi_english: 'Taurus', longitude: 45, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            venus: { name_sanskrit: 'Shukra', name_english: 'Venus', rashi_english: 'Pisces', longitude: 356, is_retrograde: false, dignity: { state: 'exalted', strength: 'strong' } },
            saturn: { name_sanskrit: 'Shani', name_english: 'Saturn', rashi_english: 'Pisces', longitude: 1, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            rahu: { name_sanskrit: 'Rahu', name_english: 'Rahu', rashi_english: 'Pisces', longitude: 18, is_retrograde: true, dignity: { state: 'neutral', strength: 'moderate' } },
            ketu: { name_sanskrit: 'Ketu', name_english: 'Ketu', rashi_english: 'Virgo', longitude: 198, is_retrograde: true, dignity: { state: 'neutral', strength: 'moderate' } },
          },
          houses: Array.from({ length: 12 }).map((_, index) => ({ house_number: index + 1, rashi_english: `House ${index + 1}`, occupants: [] })),
          aspects: [{ from: 'ketu', to: 'rahu', aspect_degree: 180, orb: 0, strength: 1 }],
          yogas: [{ id: 'gaja_kesari', description: 'Moon and Jupiter relation' }],
          doshas: [{ id: 'manglik', description: 'Mars in key houses' }],
          consistency_checks: [{ id: 'graha_count', status: 'pass', message: 'All 9 grahas present.' }],
          dasha: {
            total_major_periods: 9,
            timeline: [{
              lord: 'venus',
              start: '2026-02-12T06:30:00+05:45',
              end: '2046-02-12T06:30:00+05:45',
              duration_years: 20,
              antar_dasha: Array.from({ length: 9 }).map((_, index) => ({ lord: `lord-${index}` })),
            }],
          },
          method_profile: 'kundali_v2_aspects_dasha',
          advisory_scope: 'astrology_assist',
        },
        meta: {},
      });
    }

    if (url.includes('/feeds/next')) {
      return jsonResponse({ data: { events: [] }, meta: {} });
    }

    return jsonResponse({ data: {}, meta: {} });
  });
}

describe('App routing', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', buildFetchMock());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('loads explorer by default and navigates to panchanga page', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Festival Explorer/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('link', { name: /Panchanga/i }));

    expect(await screen.findByRole('heading', { name: /Panchanga Viewer/i })).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: /Panchanga Response Authority/i })).toBeInTheDocument();
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/calendar/panchanga?date='),
        expect.any(Object),
      );
    });
  });

  it('navigates through personal, muhurta, and kundali pages', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Festival Explorer/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('link', { name: /Personal/i }));
    expect(await screen.findByRole('heading', { name: /Personal Panchanga/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('link', { name: /Muhurta/i }));
    expect(await screen.findByRole('heading', { name: /Muhurta Finder/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('link', { name: /Kundali/i }));
    expect(await screen.findByRole('heading', { name: /Kundali Studio/i })).toBeInTheDocument();

  });
});
