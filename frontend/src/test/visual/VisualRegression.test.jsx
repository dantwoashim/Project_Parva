import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../../App';

const routeLoadOptions = { timeout: 15000 };

function setViewport(width, height = 900) {
  window.innerWidth = width;
  window.innerHeight = height;
}

function response(payload) {
  return {
    ok: true,
    status: 200,
    statusText: 'OK',
    headers: { get: () => 'application/json' },
    json: async () => payload,
    text: async () => JSON.stringify(payload),
  };
}

function buildVisualFetchMock() {
  return vi.fn(async (input) => {
    const url = String(input);

    if (url.includes('/festivals/dashain/dates?')) {
      return response({
        data: {
          dates: [
            {
              gregorian_year: 2026,
              start_date: '2026-10-20',
              end_date: '2026-10-30',
              bs_start: { formatted: '2083 Ashwin 4' },
              bs_end: { formatted: '2083 Ashwin 14' },
            },
            {
              gregorian_year: 2027,
              start_date: '2027-10-10',
              end_date: '2027-10-20',
              bs_start: { formatted: '2084 Ashwin 23' },
              bs_end: { formatted: '2084 Kartik 2' },
            },
          ],
        },
        meta: {},
      });
    }

    if (url.includes('/festivals/dashain')) {
      return response({
        data: {
          festival: {
            id: 'dashain',
            name: 'Dashain',
            name_nepali: 'Dasain',
            category: 'national',
            calendar_system: 'Lunisolar profile',
            duration_days: 10,
            significance_level: 5,
            description: 'Dashain gathers family, blessing, and renewal into the largest festival rhythm in Nepal.',
            tagline: 'Blessing, reunion, and seasonal turning gathered into one long observance.',
            mythology: {
              summary: 'The observance is commonly tied to renewal, protection, and blessing.',
              significance: 'Families mark the season through blessing, homecoming, and ritual continuity across generations.',
            },
            ritual_sequence: {
              days: [
                {
                  name: 'Ghatasthapana',
                  significance: 'The observance begins by establishing sacred space and invoking protective presence.',
                  events: [
                    {
                      title: 'Kalash Sthapana',
                      description: 'A ritual vessel and barley planting begin the seasonal sequence.',
                    },
                  ],
                },
                {
                  name: 'Maha Ashtami',
                  significance: 'The household rhythm intensifies around worship, preparation, and offering.',
                  events: [
                    {
                      title: 'Durga Puja',
                      description: 'Families and temples observe the protecting form of the goddess.',
                    },
                  ],
                },
              ],
            },
            regions: ['Kathmandu Valley', 'Nationwide'],
            deities: ['Durga'],
            calculation_method: 'lunisolar festival profile',
          },
          dates: {
            start_date: '2026-10-20',
            end_date: '2026-10-30',
            bs_start: { formatted: '2083 Ashwin 4' },
            bs_end: { formatted: '2083 Ashwin 14' },
            confidence: 'computed',
            calculation_method: 'lunisolar festival profile',
          },
          nearby_festivals: [
            { id: 'indra-jatra', name: 'Indra Jatra', category: 'newari' },
            { id: 'tihar', name: 'Tihar', category: 'national' },
          ],
        },
        meta: {
          quality_band: 'computed',
          confidence: { level: 'computed' },
        },
      });
    }

    if (url.includes('/festivals/upcoming?')) {
      return response({
        data: {
          festivals: [
            { id: 'dashain', name: 'Dashain', category: 'national', start_date: '2026-10-20' },
            { id: 'tihar', name: 'Tihar', category: 'national', start_date: '2026-11-07' },
            { id: 'chhath', name: 'Chhath', category: 'regional', start_date: '2026-11-18' },
          ],
        },
        meta: {},
      });
    }

    if (url.includes('/temporal/compass')) {
      return response({
        data: {
          date: '2026-02-25',
          location: {
            latitude: 27.7172,
            longitude: 85.324,
            timezone: 'Asia/Kathmandu',
          },
          bikram_sambat: { year: 2082, month_name: 'Falgun', day: 3 },
          primary_readout: { tithi_name: 'Chaturdashi', paksha: 'krishna' },
          horizon: {
            sunrise: {
              local: '2026-02-25T06:42:00+05:45',
              utc: '2026-02-25T00:57:00Z',
              local_time: '06:42 AM',
            },
            sunset: {
              local: '2026-02-25T17:53:00+05:45',
              utc: '2026-02-25T12:08:00Z',
              local_time: '05:53 PM',
            },
            current_muhurta: {
              name: 'Abhijit Muhurta',
              start: '2026-02-25T11:48:00+05:45',
              end: '2026-02-25T12:36:00+05:45',
            },
            rahu_kalam: {
              start: '2026-02-25T16:12:00+05:45',
              end: '2026-02-25T17:00:00+05:45',
            },
          },
          today: {
            festivals: [{ id: 'dashain', name: 'Dashain' }],
            count: 1,
          },
          signals: {
            nakshatra: { name: 'Shravana' },
            yoga: { name: 'Shubha' },
            karana: { name: 'Vishti' },
            vaara: { name_english: 'Sunday' },
          },
          quality_band_filter: 'computed',
          engine: {
            method: 'ephemeris_udaya',
            method_profile: 'temporal_compass_v3',
          },
        },
        meta: {
          confidence: { level: 'computed', score: 0.95 },
          trace_id: 'tr_visual_compass',
          method: 'ephemeris_udaya',
        },
      });
    }

    if (url.includes('/festivals/timeline?')) {
      return response({
        data: {
          groups: [
            {
              month_key: '2026-10',
              month_label: 'Kartik 2083',
              items: [
                {
                  id: 'dashain',
                  name: 'Dashain',
                  display_name: 'Dashain',
                  category: 'national',
                  start_date: '2026-10-20',
                  end_date: '2026-10-30',
                  quality_band: 'computed',
                  summary: 'Blessing, reunion, and seasonal turning gathered into one long observance.',
                  regional_focus: ['Nepal'],
                },
                {
                  id: 'tihar',
                  name: 'Tihar',
                  display_name: 'Tihar',
                  category: 'national',
                  start_date: '2026-11-07',
                  end_date: '2026-11-11',
                  quality_band: 'computed',
                  summary: 'Festival of lights with layered family and household observance.',
                  regional_focus: ['Kathmandu Valley'],
                },
              ],
            },
          ],
          facets: {
            categories: [{ value: 'national', label: 'National', count: 2 }],
            months: [{ value: '2026-10', label: 'October', count: 2 }],
            regions: [{ value: 'nepal', label: 'Nepal', count: 1 }],
          },
          calculation_trace_id: 'tr_visual_timeline',
        },
        meta: {},
      });
    }

    if (url.includes('/festivals/on-date/')) {
      return response({ data: [{ id: 'dashain', name: 'Dashain' }], meta: {} });
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
          calculation_trace_id: 'tr_visual_panchanga',
        },
        meta: {
          confidence: { level: 'computed', score: 0.92 },
          trace_id: 'tr_visual_panchanga',
          method: 'ephemeris_udaya',
        },
      });
    }

    if (url.includes('/resolve?')) {
      return response({ data: { trace: { trace_id: 'tr_visual_resolve' } }, meta: {} });
    }

    if (url.includes('/personal/panchanga')) {
      return response({
        data: {
          date: '2026-02-15',
          bikram_sambat: { year: 2082, month: 11, day: 3, month_name: 'Falgun' },
          tithi: { number: 14, name: 'Chaturdashi', paksha: 'krishna' },
          nakshatra: { number: 22, name: 'Shravana' },
          yoga: { number: 9, name: 'Shubha' },
          karana: { number: 7, name: 'Vishti' },
          vaara: { name_english: 'Sunday', name_sanskrit: 'Ravivara' },
          location: { latitude: 27.7172, longitude: 85.324, timezone: 'Asia/Kathmandu' },
          local_sunrise: {
            local: '2026-02-15T06:44:00+05:45',
            utc: '2026-02-15T00:59:00Z',
            local_time: '06:44 AM',
          },
          sunrise: {
            local: '2026-02-15T06:42:00+05:45',
            utc: '2026-02-15T00:57:00Z',
            local_time: '06:42 AM',
          },
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

    if (url.includes('/personal/context')) {
      return response({
        data: {
          date: '2026-02-25',
          location: { latitude: 27.7172, longitude: 85.324, timezone: 'Asia/Kathmandu' },
          place_title: 'Kyoto Villa',
          status_line: 'Sunrise 6:44 AM - Asia/Kathmandu',
          visit_note: 'Last visited Oct 15. Next reminder: Cherry Blossom (Apr).',
          context_title: 'Morning Calm',
          context_summary: 'Quiet morning at your saved Kyoto Villa location. Air is crisp. 14C.',
          daily_inspiration: 'The soul sits here, in the quiet spaces we keep. - A. Chen.',
          upcoming_reminders: [{ id: 'gion-matsuri', title: 'Gion Matsuri', date_label: 'Jul 1-31', status: 'Active' }],
        },
        meta: {},
      });
    }

    if (url.includes('/muhurta/heatmap')) {
      return response({
        data: {
          date: '2026-02-25',
          location: {
            latitude: 27.7172,
            longitude: 85.324,
            timezone: 'Asia/Kathmandu',
          },
          type: 'general',
          assumption_set_id: 'np-mainstream-v2',
          sunrise: {
            local: '2026-02-25T06:42:00+05:45',
            utc: '2026-02-25T00:57:00Z',
            local_time: '06:42 AM',
          },
          sunset: {
            local: '2026-02-25T17:53:00+05:45',
            utc: '2026-02-25T12:08:00Z',
            local_time: '05:53 PM',
          },
          blocks: [
            {
              index: 6,
              name: 'Abhijit Muhurta',
              class: 'auspicious',
              score: 88,
              start: '2026-02-15T11:48:00+05:45',
              end: '2026-02-15T12:36:00+05:45',
              confidence_score: 0.91,
              reason_codes: ['hora_supportive', 'tara_good'],
              rank_explanation: 'Strong overlap of supportive factors.',
            },
            {
              index: 7,
              name: 'Labh',
              class: 'mixed',
              score: 42,
              start: '2026-02-15T12:36:00+05:45',
              end: '2026-02-15T13:24:00+05:45',
              confidence_score: 0.75,
              reason_codes: ['tara_good'],
              rank_explanation: 'Supportive but not as strong as the lead window.',
            },
          ],
          best_window: {
            index: 6,
            name: 'Abhijit Muhurta',
            score: 88,
            start: '2026-02-15T11:48:00+05:45',
            end: '2026-02-15T12:36:00+05:45',
            confidence_score: 0.91,
            reason_codes: ['hora_supportive', 'tara_good'],
          },
          rahu_kalam: { segment: 8, start: '2026-02-15T16:12:00+05:45', end: '2026-02-15T17:00:00+05:45' },
          calculation_trace_id: 'tr_muhurta_visual',
        },
        meta: {},
      });
    }

    if (url.includes('/kundali/graph')) {
      return response({
        data: {
          datetime: '2026-02-25T06:30:00+05:45',
          location: {
            latitude: 27.7172,
            longitude: 85.324,
            timezone: 'Asia/Kathmandu',
          },
          layout: {
            viewbox: '0 0 320 320',
            house_nodes: [
              { id: 'house_1', label: '1', x: 70, y: 70 },
              { id: 'house_7', label: '7', x: 250, y: 250 },
            ],
            graha_nodes: [
              { id: 'mars', label: 'Mars', x: 120, y: 90, house_id: 'house_1' },
              { id: 'venus', label: 'Venus', x: 220, y: 210, house_id: 'house_7' },
            ],
            aspect_edges: [{ id: 'asp_1', source: 'mars', target: 'venus', type: 'trine' }],
          },
          insight_blocks: [{ id: 'ins_1', title: 'Mars-Venus link', summary: 'Supportive trinal relation in this profile.' }],
          calculation_trace_id: 'tr_kundali_graph_visual',
        },
        meta: {},
      });
    }

    if (url.includes('/kundali') && !url.includes('/kundali/graph') && !url.includes('/kundali/lagna')) {
      return response({
        data: {
          lagna: { rashi_english: 'Pisces', rashi_sanskrit: 'Meena', longitude: 12.2 },
          grahas: {
            mars: { name_english: 'Mars', name_sanskrit: 'Mangala', rashi_english: 'Cancer', longitude: 102.4, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            sun: { name_english: 'Sun', name_sanskrit: 'Surya', rashi_english: 'Aquarius', longitude: 332.1, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
            moon: { name_english: 'Moon', name_sanskrit: 'Chandra', rashi_english: 'Capricorn', longitude: 289.3, is_retrograde: false, dignity: { state: 'neutral', strength: 'moderate' } },
          },
          houses: Array.from({ length: 12 }).map((_, index) => ({ house_number: index + 1, rashi_english: `House ${index + 1}`, occupants: [] })),
          aspects: [{ from: 'mars', to: 'venus', aspect_degree: 120, orb: 0.8, strength: 0.92 }],
          yogas: [{ id: 'gaja_kesari', description: 'Moon and Jupiter in kendra relation.' }],
          doshas: [{ id: 'manglik', description: 'Mars influence in sensitive houses.' }],
          consistency_checks: [{ id: 'graha_count', status: 'pass', message: 'All 9 grahas present.' }],
          dasha: { total_major_periods: 9, timeline: [] },
          insight_blocks: [{ id: 'i1', title: 'Lagna baseline', summary: 'Pisces lagna reflects the reference profile.' }],
          method_profile: 'kundali_v2_aspects_dasha',
          quality_band: 'validated',
          advisory_scope: 'astrology_assist',
          confidence: 'computed',
          calculation_trace_id: 'tr_kundali_visual',
        },
        meta: {},
      });
    }

    if (url.includes('/glossary?')) {
      return response({
        data: {
          content: {
            title: 'Glossary',
            intro: 'Reference glossary payload for visual snapshots.',
            sections: [
              {
                id: 'core',
                title: 'Core Terms',
                terms: [{ name: 'Tithi', meaning: 'Lunar day', why_it_matters: 'Used to determine observance timing.' }],
              },
            ],
          },
        },
        meta: {},
      });
    }

    if (url.includes('/feeds/next')) {
      return response({ data: { events: [] }, meta: {} });
    }

    if (url.includes('/festivals/coverage/scoreboard')) {
      return response({ data: { score: 100 }, meta: {} });
    }

    if (url.includes('/festivals?')) {
      return response({
        data: {
          festivals: [
            { id: 'dashain', name: 'Dashain', category: 'national' },
            { id: 'tihar', name: 'Tihar', category: 'national' },
          ],
          total: 2,
        },
        meta: {},
      });
    }

    return response({ data: {}, meta: {} });
  });
}

async function renderRoute(route, width = 1024, height = 900) {
  setViewport(width, height);
  return render(
    <MemoryRouter initialEntries={[route]}>
      <App />
    </MemoryRouter>,
  );
}

describe('visual regression harness', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', buildVisualFetchMock());
    vi.stubGlobal('open', vi.fn());
    vi.spyOn(Date, 'now').mockReturnValue(new Date('2026-02-25T06:30:00Z').valueOf());
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('consumer home visual baseline', async () => {
    const { container } = await renderRoute('/');
    await screen.findByRole('heading', { name: /Upcoming Festivals/i }, routeLoadOptions);
    expect(container.querySelector('.almanac-home')).toMatchSnapshot();
  }, 15000);

  it('today page visual baseline on mobile', async () => {
    const { container } = await renderRoute('/today', 390, 844);
    await screen.findByRole('heading', { name: /Today in Kathmandu/i }, routeLoadOptions);
    expect(container.querySelector('.today-page')).toMatchSnapshot();
  }, 15000);

  it('best-time page visual baseline on mobile', async () => {
    const { container } = await renderRoute('/best-time', 390, 844);
    await screen.findByRole('heading', { name: /Muhurta Explorer/i }, routeLoadOptions);
    expect(container.querySelector('.muhurta-page')).toMatchSnapshot();
  }, 15000);

  it('festivals page visual baseline on mobile', async () => {
    const { container } = await renderRoute('/festivals', 390, 844);
    await screen.findByRole('heading', { name: /Festival\s*Explorer/i }, routeLoadOptions);
    expect(container.querySelector('.explorer-page')).toMatchSnapshot();
  }, 15000);

  it('festival detail page visual baseline on mobile', async () => {
    const { container } = await renderRoute('/festivals/dashain', 390, 844);
    await screen.findByRole('heading', { name: 'Dashain' }, routeLoadOptions);
    await screen.findByRole('heading', { name: /The Ritual Timeline/i }, routeLoadOptions);
    expect(container.querySelector('.festival-detail')).toMatchSnapshot();
  }, 15000);

  it('my-place page visual baseline on mobile', async () => {
    const { container } = await renderRoute('/my-place', 390, 844);
    await screen.findByRole('heading', { name: /Keep the place that changes your day in view/i }, routeLoadOptions);
    expect(container.querySelector('.personal-page')).toMatchSnapshot();
  }, 15000);

  it('kundali page visual baseline', async () => {
    const { container } = await renderRoute('/kundali');
    await screen.findByRole('heading', { name: /Janma Kundali/i }, routeLoadOptions);
    await screen.findByRole('heading', { name: /The reading in plain language/i }, routeLoadOptions);
    expect(container.querySelector('.kundali-editorial')).toMatchSnapshot();
  }, 20000);

  it('today page visual baseline on desktop', async () => {
    const { container } = await renderRoute('/today', 1440, 900);
    await screen.findByRole('heading', { name: /Today in Kathmandu/i }, routeLoadOptions);
    expect(container.querySelector('.app-shell')).toMatchSnapshot();
  }, 15000);

  it('festivals page visual baseline on desktop', async () => {
    const { container } = await renderRoute('/festivals', 1440, 900);
    await screen.findByRole('heading', { name: /Festival\s*Explorer/i }, routeLoadOptions);
    expect(container.querySelector('.app-shell')).toMatchSnapshot();
  }, 15000);

  it('festival detail page visual baseline on desktop', async () => {
    const { container } = await renderRoute('/festivals/dashain', 1440, 900);
    await screen.findByRole('heading', { name: 'Dashain' }, routeLoadOptions);
    expect(container.querySelector('.app-shell')).toMatchSnapshot();
  }, 15000);

  it('best-time page visual baseline on desktop', async () => {
    const { container } = await renderRoute('/best-time', 1440, 900);
    await screen.findByRole('heading', { name: /Muhurta Explorer/i }, routeLoadOptions);
    expect(container.querySelector('.app-shell')).toMatchSnapshot();
  }, 15000);

  it('my-place page visual baseline on desktop', async () => {
    const { container } = await renderRoute('/my-place', 1440, 900);
    await screen.findByRole('heading', { name: /Keep the place that changes your day in view/i }, routeLoadOptions);
    expect(container.querySelector('.app-shell')).toMatchSnapshot();
  }, 15000);
});
