import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../../App';

function response(payload) {
  return {
    ok: true,
    status: 200,
    statusText: 'OK',
    json: async () => payload,
    text: async () => JSON.stringify(payload),
  };
}

function buildVisualFetchMock() {
  return vi.fn(async (input) => {
    const url = String(input);

    if (url.includes('/festivals/coverage/scoreboard')) {
      return response({
        data: {
          computed: { count: 323, pct: 71.3 },
          provisional: { count: 111, pct: 24.5 },
          inventory: { count: 19, pct: 4.2 },
          claim_guard: { headline_metric: 'computed', safe_to_claim_300: true },
        },
        meta: {},
      });
    }

    if (url.includes('/festivals?')) {
      return response({
        data: {
          festivals: [
            {
              id: 'dashain',
              name: 'Dashain',
              name_nepali: 'दशैं',
              category: 'national',
              duration_days: 10,
              next_occurrence: '2026-10-20',
              significance_level: 5,
              primary_color: '#C85A3E',
              validation_band: 'gold',
              rule_status: 'computed',
            },
            {
              id: 'tihar',
              name: 'Tihar',
              name_nepali: 'तिहार',
              category: 'national',
              duration_days: 5,
              next_occurrence: '2026-11-07',
              significance_level: 4,
              primary_color: '#D4A052',
              validation_band: 'validated',
              rule_status: 'computed',
            },
          ],
          total: 2,
        },
        meta: {},
      });
    }

    if (url.includes('/calendar/panchanga?')) {
      return response({
        data: {
          date: '2026-02-15',
          bikram_sambat: { year: 2082, month: 11, day: 3, month_name: 'Falgun' },
          panchanga: {
            confidence: 'astronomical',
            tithi: { number: 14, name: 'Chaturdashi', paksha: 'krishna', method: 'ephemeris_udaya', sunrise_used: '2026-02-15T06:43:00+05:45' },
            nakshatra: { name: 'Shravana', pada: 1 },
            yoga: { name: 'Shubha', number: 9 },
            karana: { name: 'Vishti', number: 7 },
            vaara: { name_english: 'Sunday', name_sanskrit: 'Ravivara' },
          },
          ephemeris: { mode: 'swiss_moshier' },
        },
        meta: {
          confidence: { level: 'computed', score: 0.92 },
          trace_id: 'tr_visual_001',
          method: 'ephemeris_udaya',
          provenance: { snapshot_id: 'snap_visual', dataset_hash: 'sha256:abc', rules_hash: 'sha256:def', verify_url: '/verify/tr_visual_001' },
          uncertainty: { boundary_risk: 'low', interval_hours: 0.5 },
          policy: { profile: 'np-mainstream', jurisdiction: 'NP', advisory: true },
        },
      });
    }

    if (url.includes('/personal/panchanga?')) {
      return response({
        data: {
          date: '2026-02-15',
          bikram_sambat: { year: 2082, month: 11, day: 3, month_name: 'Falgun' },
          tithi: { number: 14, name: 'Chaturdashi', paksha: 'krishna' },
          nakshatra: { number: 22, name: 'Shravana' },
          yoga: { number: 9, name: 'Shubha' },
          karana: { number: 7, name: 'Vishti' },
          vaara: { name_english: 'Sunday', name_sanskrit: 'Ravivara' },
          location: { latitude: 27.7172, longitude: 85.3240, timezone: 'Asia/Kathmandu' },
          confidence: 'computed',
          method_profile: 'personal_panchanga_v2_udaya',
          quality_band: 'gold',
          advisory_scope: 'ritual_planning',
          assumption_set_id: 'np-personal-panchanga-v2',
          calculation_trace_id: 'tr_personal_visual',
        },
        meta: {},
      });
    }

    if (url.includes('/muhurta/auspicious?')) {
      return response({
        data: {
          method_profile: 'muhurta_v2_hora_chaughadia_tarabala',
          assumption_set_id: 'np-mainstream-v2',
          best_window: {
            number: 7,
            name: 'Abhijit Muhurta',
            start: '11:48',
            end: '12:36',
            score: 88,
          },
          ranked_muhurtas: [
            { number: 7, name: 'Abhijit Muhurta', score: 88, hora: { lord_display: 'Jupiter' }, chaughadia: { name_display: 'Labh' } },
            { number: 10, name: 'Shubha Muhurta', score: 75, hora: { lord_display: 'Venus' }, chaughadia: { name_display: 'Amrit' } }
          ],
          muhurtas: [
            { number: 7, index: 6, name: 'Abhijit Muhurta', start: '11:48', end: '12:36', score: 88, hora: { lord_display: 'Jupiter' }, chaughadia: { name_display: 'Labh' } },
            { number: 10, index: 9, name: 'Shubha Muhurta', start: '14:12', end: '15:00', score: 75, hora: { lord_display: 'Venus' }, chaughadia: { name_display: 'Amrit' } }
          ],
          tara_bala: { quality: 'good', tara: { name: 'Sampat', distance: 2 } },
          warnings: [],
        },
        meta: {},
      });
    }

    if (url.includes('/muhurta/rahu-kalam?')) {
      return response({
        data: {
          weekday: 'Sunday',
          rahu_kalam: {
            segment: 8,
            start: '16:12',
            end: '17:00'
          }
        },
        meta: {},
      });
    }

    if (url.includes('/muhurta?')) {
      return response({
        data: {
          day_muhurtas: Array.from({ length: 15 }).map((_, index) => ({ number: index + 1, name: `Day Muhurta ${index + 1}` })),
          night_muhurtas: Array.from({ length: 15 }).map((_, index) => ({ number: index + 16, name: `Night Muhurta ${index + 16}` })),
          muhurtas: Array.from({ length: 30 }).map((_, index) => ({ number: index + 1, name: `Muhurta ${index + 1}`, duration_minutes: 48 })),
          hora: {
            day: Array.from({ length: 12 }).map((_, index) => ({ number: index + 1, lord_display: 'Sun' })),
            night: Array.from({ length: 12 }).map((_, index) => ({ number: index + 1, lord_display: 'Moon' })),
          },
          chaughadia: {
            day: Array.from({ length: 8 }).map((_, index) => ({ number: index + 1, name_display: 'Labh' })),
            night: Array.from({ length: 8 }).map((_, index) => ({ number: index + 1, name_display: 'Amrit' })),
          },
          daylight_minutes: 720,
          night_minutes: 720,
          tara_bala: { quality: 'neutral' },
          method_profile: 'muhurta_v2_hora_chaughadia_tarabala',
          quality_band: 'validated',
        },
        meta: {},
      });
    }

    if (url.includes('/kundali?')) {
      return response({
        data: {
          lagna: { rashi_english: 'Pisces', rashi_sanskrit: 'Meena', longitude: 12.2 },
          grahas: {
            mars: { name_english: 'Mars', name_sanskrit: 'Mangala', rashi_english: 'Cancer', longitude: 102.4, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            sun: { name_english: 'Sun', name_sanskrit: 'Surya', rashi_english: 'Aquarius', longitude: 332.1, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            moon: { name_english: 'Moon', name_sanskrit: 'Chandra', rashi_english: 'Capricorn', longitude: 289.3, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            mercury: { name_english: 'Mercury', name_sanskrit: 'Budha', rashi_english: 'Aquarius', longitude: 325.0, is_retrograde: false, dignity: { state: 'own', strength: 'strong' } },
            jupiter: { name_english: 'Jupiter', name_sanskrit: 'Guru', rashi_english: 'Taurus', longitude: 45.8, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            venus: { name_english: 'Venus', name_sanskrit: 'Shukra', rashi_english: 'Pisces', longitude: 356.2, is_retrograde: false, dignity: { state: 'exalted', strength: 'strong' } },
            saturn: { name_english: 'Saturn', name_sanskrit: 'Shani', rashi_english: 'Pisces', longitude: 1.6, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            rahu: { name_english: 'Rahu', name_sanskrit: 'Rahu', rashi_english: 'Pisces', longitude: 18.1, is_retrograde: true, dignity: { state: 'neutral', strength: 'moderate' } },
            ketu: { name_english: 'Ketu', name_sanskrit: 'Ketu', rashi_english: 'Virgo', longitude: 198.1, is_retrograde: true, dignity: { state: 'neutral', strength: 'moderate' } }
          },
          houses: Array.from({ length: 12 }).map((_, index) => ({ house_number: index + 1, rashi_english: `House ${index + 1}`, occupants: [] })),
          aspects: [
            { from: 'ketu', to: 'rahu', aspect_degree: 180, orb: 0, strength: 1.0 }
          ],
          yogas: [{ id: 'gaja_kesari', description: 'Moon and Jupiter in kendra relation.' }],
          doshas: [{ id: 'manglik', description: 'Mars influences marriage-sensitive houses.' }],
          consistency_checks: [{ id: 'graha_count', status: 'pass', message: 'All 9 grahas present.' }],
          dasha: {
            total_major_periods: 9,
            timeline: [{
              lord: 'venus',
              start: '2026-02-15T06:30:00+05:45',
              end: '2046-02-15T06:30:00+05:45',
              duration_years: 20,
              antar_dasha: [
                { lord: 'venus', start: '2026-02-15T06:30:00+05:45', end: '2029-02-15T06:30:00+05:45', duration_years: 3.0 },
                { lord: 'sun', start: '2029-02-15T06:30:00+05:45', end: '2030-02-15T06:30:00+05:45', duration_years: 1.0 },
                { lord: 'moon', start: '2030-02-15T06:30:00+05:45', end: '2032-02-15T06:30:00+05:45', duration_years: 2.0 }
              ]
            }]
          },
          method_profile: 'kundali_v2_aspects_dasha',
          quality_band: 'validated',
          advisory_scope: 'astrology_assist',
          confidence: 'computed',
          calculation_trace_id: 'tr_kundali_visual'
        },
        meta: {},
      });
    }

    if (url.includes('/resolve?')) {
      return response({
        data: {
          trace: {
            trace_id: 'tr_visual_001',
            explain: 'Visual regression fixture',
          },
        },
        meta: { trace_id: 'tr_visual_001' },
      });
    }

    if (url.includes('/feeds/next')) {
      return response({ data: { events: [] }, meta: {} });
    }

    return response({ data: {}, meta: {} });
  });
}

async function renderRoute(route) {
  const rendered = render(
    <MemoryRouter initialEntries={[route]}>
      <App />
    </MemoryRouter>,
  );
  return rendered;
}

describe('visual regression harness', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', buildVisualFetchMock());
    vi.stubGlobal('open', vi.fn());
    vi.spyOn(Date, 'now').mockReturnValue(new Date('2026-02-18T00:45:00Z').valueOf());
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('explorer page visual baseline', async () => {
    const { container } = await renderRoute('/');
    await screen.findByRole('heading', { name: /Festival Explorer/i });
    expect(container.querySelector('.explorer-page')).toMatchSnapshot();
  });

  it('panchanga page visual baseline', async () => {
    const { container } = await renderRoute('/panchanga');
    await screen.findByRole('heading', { name: /Panchanga Viewer/i });
    expect(container.querySelector('.panchanga-page')).toMatchSnapshot();
  });

  it('feeds page visual baseline', async () => {
    const { container } = await renderRoute('/feeds');
    await screen.findByRole('heading', { name: /iCal Subscriptions/i });
    expect(container.querySelector('.feeds-page')).toMatchSnapshot();
  });


  it('personal page visual baseline', async () => {
    const { container } = await renderRoute('/personal');
    await screen.findByRole('heading', { name: /Personal Panchanga/i });
    expect(container.querySelector('.personal-page')).toMatchSnapshot();
  });

  it('muhurta page visual baseline', async () => {
    const { container } = await renderRoute('/muhurta');
    await screen.findByRole('heading', { name: /Muhurta Finder/i });
    expect(container.querySelector('.muhurta-page')).toMatchSnapshot();
  });

  it('kundali page visual baseline', async () => {
    const { container } = await renderRoute('/kundali');
    await screen.findByRole('heading', { name: /Kundali Studio/i });
    expect(container.querySelector('.kundali-page')).toMatchSnapshot();
  });
});
