import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

const routeLoadOptions = { timeout: 15000 };

function setViewportWidth(width) {
  window.innerWidth = width;
  window.dispatchEvent(new Event('resize'));
}

function createMemoryStorage() {
  const backing = new Map();

  return {
    getItem: vi.fn((key) => (backing.has(key) ? backing.get(key) : null)),
    setItem: vi.fn((key, value) => {
      backing.set(key, String(value));
    }),
    removeItem: vi.fn((key) => {
      backing.delete(key);
    }),
    clear: vi.fn(() => {
      backing.clear();
    }),
  };
}

function jsonResponse(payload) {
  return {
    ok: true,
    status: 200,
    statusText: 'OK',
    headers: { get: () => 'application/json' },
    json: async () => payload,
    text: async () => JSON.stringify(payload),
  };
}

function buildCompassEnvelope(overrides = {}) {
  return {
    data: {
      date: '2026-02-15',
      location: {
        latitude: 27.7172,
        longitude: 85.324,
        timezone: 'Asia/Kathmandu',
      },
      bikram_sambat: {
        year: 2082,
        month: 11,
        day: 3,
        month_name: 'Falgun',
      },
      primary_readout: {
        tithi_name: 'Chaturdashi',
        tithi_number: 14,
        paksha: 'krishna',
      },
      horizon: {
        sunrise: {
          local: '2026-02-15T06:42:00+05:45',
          utc: '2026-02-15T00:57:00Z',
          local_time: '06:42 AM',
        },
        sunset: {
          local: '2026-02-15T17:53:00+05:45',
          utc: '2026-02-15T12:08:00Z',
          local_time: '05:53 PM',
        },
        current_muhurta: {
          name: 'Abhijit Muhurta',
          start: '2026-02-15T10:30:00+05:45',
          end: '2026-02-15T12:15:00+05:45',
          score: 88,
          class: 'auspicious',
        },
        rahu_kalam: {
          start: '2026-02-15T13:15:00+05:45',
          end: '2026-02-15T14:30:00+05:45',
        },
      },
      today: {
        festivals: [],
        count: 0,
      },
      signals: {
        nakshatra: { name: 'Shravana', pada: 1 },
        yoga: { name: 'Shubha' },
        karana: { name: 'Vishti' },
        vaara: { name_english: 'Sunday' },
      },
      quality_band_filter: 'computed',
      engine: {
        method: 'ephemeris_udaya',
        method_profile: 'temporal_compass_v1',
      },
      ...overrides.data,
    },
    meta: {
      method: 'ephemeris_udaya',
      confidence: { level: 'high' },
      ...overrides.meta,
    },
  };
}

function buildHeatmapEnvelope(overrides = {}) {
  return {
    data: {
      date: '2026-02-15',
      location: {
        latitude: 27.7172,
        longitude: 85.324,
        timezone: 'Asia/Kathmandu',
      },
      type: 'general',
      assumption_set_id: 'np-mainstream-v2',
      best_window: {
        index: 6,
        name: 'Abhijit Muhurta',
        start: '2026-02-15T10:30:00+05:45',
        end: '2026-02-15T12:15:00+05:45',
        score: 88,
      },
      blocks: [
        {
          index: 6,
          name: 'Abhijit Muhurta',
          class: 'auspicious',
          score: 88,
          start: '2026-02-15T10:30:00+05:45',
          end: '2026-02-15T12:15:00+05:45',
          reason_codes: ['tara_good', 'hora_supportive'],
        },
        {
          index: 7,
          name: 'Labh',
          class: 'mixed',
          score: 41,
          start: '2026-02-15T15:45:00+05:45',
          end: '2026-02-15T17:00:00+05:45',
          reason_codes: [],
        },
      ],
      rahu_kalam: {
        start: '2026-02-15T13:15:00+05:45',
        end: '2026-02-15T14:30:00+05:45',
      },
      sunrise: '2026-02-15T06:42:00+05:45',
      sunset: '2026-02-15T17:53:00+05:45',
      ranking_profile: { minimum_score: 25 },
      tara_bala: { status: 'neutral' },
      ...overrides.data,
    },
    meta: {
      method: 'rule_ranked_muhurta_v2',
      confidence: { level: 'high' },
      ...overrides.meta,
    },
  };
}

function buildCalendarPayload(fromDate = '2026-02-01', toDate = '2026-03-31') {
  return {
    from: fromDate,
    to: toDate,
    location: {
      latitude: 27.7172,
      longitude: 85.324,
      timezone: 'Asia/Kathmandu',
    },
    type: 'general',
    assumption_set_id: 'np-mainstream-v2',
    days: [
      {
        date: fromDate,
        has_viable_window: true,
        minimum_score: 25,
        top_score: 88,
        tone: 'strong',
        window_count: 3,
        best_window: {
          index: 6,
          name: 'Abhijit Muhurta',
          start: `${fromDate}T10:30:00+05:45`,
          end: `${fromDate}T12:15:00+05:45`,
          score: 88,
          quality: 'auspicious',
          reason_codes: ['tara_good'],
          rank_explanation: 'One of the clearest dates in the current planning range.',
        },
        caution: {
          rahu_kalam: {
            start: `${fromDate}T13:15:00+05:45`,
            end: `${fromDate}T14:30:00+05:45`,
          },
        },
      },
    ],
    total: 1,
  };
}

function buildPersonalContextEnvelope(overrides = {}) {
  return {
    data: {
      date: '2026-02-15',
      location: {
        latitude: 27.7172,
        longitude: 85.324,
        timezone: 'Asia/Kathmandu',
      },
      place_title: 'Kyoto Villa',
      status_line: 'Sunrise 6:45 AM - Asia/Kathmandu',
      visit_note: 'Last visited Oct 15. Next reminder: Cherry Blossom (Apr).',
      context_title: 'Morning Calm',
      context_summary: 'Quiet morning at your saved Kyoto Villa location. Air is crisp. 14C.',
      temperature_note: 'Air is crisp. 14C.',
      daily_inspiration: 'The soul sits here, in the quiet spaces we keep. - A. Chen.',
      upcoming_reminders: [{ id: 'gion-matsuri', title: 'Gion Matsuri', date_label: 'Jul 1-31', status: 'Active' }],
      ...overrides.data,
    },
    meta: {
      method: 'personal_context_synthesis',
      confidence: { level: 'high' },
      ...overrides.meta,
    },
  };
}

function buildKundaliGraphEnvelope(overrides = {}) {
  return {
    data: {
      datetime: '2026-02-15T06:30:00+05:45',
      location: {
        latitude: 27.7172,
        longitude: 85.324,
        timezone: 'Asia/Kathmandu',
      },
      lagna: {
        rashi_english: 'Pisces',
      },
      layout: {
        viewbox: '0 0 400 400',
        house_nodes: [
          { id: 'house_1', house_number: 1, x: 200, y: 60 },
          { id: 'house_7', house_number: 7, x: 200, y: 340 },
        ],
        graha_nodes: [
          { id: 'mars', label: 'Mars', x: 120, y: 90 },
          { id: 'venus', label: 'Venus', x: 220, y: 210 },
        ],
        aspect_edges: [{ id: 'asp_1', source: 'mars', target: 'venus', type: 'trine' }],
      },
      insight_blocks: [{ id: 'ins_1', title: 'Mars-Venus link', summary: 'Supportive trinal relation in this profile.' }],
      ...overrides.data,
    },
    meta: {
      method: 'swiss_ephemeris_sidereal',
      confidence: { level: 'high' },
      ...overrides.meta,
    },
  };
}

function buildFetchMock() {
  return vi.fn(async (input) => {
    const url = String(input);

    if (url.includes('/temporal/compass')) {
      return jsonResponse(buildCompassEnvelope());
    }

    if (url.includes('/muhurta/heatmap')) {
      return jsonResponse(buildHeatmapEnvelope());
    }

    if (url.includes('/muhurta/calendar')) {
      const parsed = new URL(url, 'https://example.test');
      return jsonResponse(buildCalendarPayload(
        parsed.searchParams.get('from') || '2026-02-01',
        parsed.searchParams.get('to') || '2026-03-31',
      ));
    }

    if (url.includes('/festivals/timeline?')) {
      return jsonResponse({
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
                  summary: 'Blessing, reunion, and seasonal turning gathered into one long observance.',
                  regional_focus: ['Nepal'],
                },
                {
                  id: 'tihar',
                  name: 'Tihar',
                  display_name: 'Tihar',
                  category: 'national',
                  start_date: '2026-11-07',
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
        },
        meta: {},
      });
    }

    if (url.includes('/festivals/dashain/dates?')) {
      return jsonResponse({
        data: {
          dates: [
            {
              gregorian_year: 2026,
              start_date: '2026-10-20',
              end_date: '2026-10-30',
              bs_start: { formatted: '2083 Ashwin 4' },
            },
          ],
        },
        meta: {},
      });
    }

    if (url.includes('/festivals/dashain')) {
      return jsonResponse({
        data: {
          festival: {
            id: 'dashain',
            name: 'Dashain',
            name_nepali: 'Dasain',
            category: 'national',
            calendar_system: 'Lunisolar profile',
            duration_days: 10,
            description: 'Dashain gathers family, blessing, and renewal into the largest festival rhythm in Nepal.',
            tagline: 'Blessing, reunion, and seasonal turning gathered into one long observance.',
            mythology: {
              summary: 'The observance is tied to renewal, protection, and family blessing.',
              significance: 'Families mark the season through blessing, homecoming, and ritual continuity across generations.',
            },
            ritual_sequence: {
              days: [
                {
                  name: 'Ghatasthapana',
                  events: [{ title: 'Kalash Sthapana', description: 'A ritual vessel and barley planting begin the seasonal sequence.' }],
                },
              ],
            },
          },
          dates: {
            start_date: '2026-10-20',
            end_date: '2026-10-30',
            calculation_method: 'lunisolar festival profile',
          },
          nearby_festivals: [
            { id: 'tihar', name: 'Tihar', category: 'national' },
          ],
        },
        meta: {},
      });
    }

    if (url.includes('/festivals/on-date/')) {
      return jsonResponse([{ id: 'dashain', name: 'Dashain', start_date: '2026-10-20' }]);
    }

    if (url.includes('/personal/context')) {
      return jsonResponse(buildPersonalContextEnvelope());
    }

    if (url.includes('/personal/panchanga')) {
      return jsonResponse({
        data: {
          date: '2026-02-15',
          location: {
            latitude: 27.7172,
            longitude: 85.324,
            timezone: 'Asia/Kathmandu',
            input_sources: {
              latitude: 'user_input',
              longitude: 'user_input',
              timezone: 'user_input',
            },
          },
          bikram_sambat: { year: 2082, month: 11, day: 3, month_name: 'Falgun' },
          tithi: { name: 'Chaturdashi', paksha: 'krishna' },
          nakshatra: { name: 'Shravana', number: 22 },
          yoga: { name: 'Shubha', number: 9 },
          vaara: { name_english: 'Sunday' },
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
          quality_band: 'computed',
        },
        meta: {},
      });
    }

    if (url.includes('/calendar/panchanga?')) {
      return jsonResponse({
        data: {
          date: '2026-02-15',
          bikram_sambat: { year: 2082, month: 11, day: 3, month_name: 'Falgun' },
          panchanga: {
            confidence: 'astronomical',
            tithi: { number: 14, name: 'Chaturdashi', paksha: 'krishna', method: 'ephemeris_udaya' },
            nakshatra: { name: 'Shravana', pada: 1 },
            yoga: { name: 'Shubha', number: 9 },
            karana: { name: 'Vishti', number: 7 },
            vaara: { name_english: 'Sunday', name_sanskrit: 'Ravivara' },
          },
          ephemeris: { mode: 'swiss_moshier' },
        },
        meta: {},
      });
    }

    if (url.includes('/resolve?')) {
      return jsonResponse({ data: { trace: { trace_id: 'tr_routes' } }, meta: {} });
    }

    if (url.includes('/festivals/upcoming?')) {
      return jsonResponse({
        data: {
          festivals: [{ id: 'dashain', name: 'Dashain', category: 'national', start_date: '2026-10-20' }],
        },
        meta: {},
      });
    }

    if (url.includes('/feeds/next')) {
      return jsonResponse({ data: { events: [] }, meta: {} });
    }

    if (url.includes('/glossary?')) {
      return jsonResponse({ data: { content: { title: 'Glossary', intro: 'Glossary intro', sections: [] } }, meta: {} });
    }

    if (url.includes('/kundali/graph')) {
      return jsonResponse(buildKundaliGraphEnvelope());
    }

    if (url.includes('/kundali') && !url.includes('/kundali/lagna')) {
      return jsonResponse({
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
          dasha: { total_major_periods: 9, timeline: [{ lord: 'Jupiter', duration_years: 16, antar_dasha: [] }] },
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

    return jsonResponse({ data: {}, meta: {} });
  });
}

describe('App routing', () => {
  beforeEach(() => {
    const storage = createMemoryStorage();
    vi.stubGlobal('localStorage', storage);
    Object.defineProperty(window, 'localStorage', {
      configurable: true,
      value: storage,
    });
    vi.stubGlobal('fetch', buildFetchMock());
    vi.stubGlobal('open', vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('renders the editorial consumer home inside the unified shell', async () => {
    setViewportWidth(1024);
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Daily Glimpse/i }, routeLoadOptions)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Upcoming Festivals/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Embrace the Divine Rhythm/i })).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: /Primary/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /For developers/i })).toHaveAttribute('href', '/developers/index.html');
  }, 30000);

  it('keeps the same consumer shell on desktop routes', async () => {
    setViewportWidth(1440);
    render(
      <MemoryRouter initialEntries={['/today']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /The rest of today in one compact pass/i }, routeLoadOptions)).toBeInTheDocument();

    const primaryNav = screen.getByRole('navigation', { name: /Primary/i });
    expect(within(primaryNav).getByRole('link', { name: /^Today$/i })).toBeInTheDocument();
    expect(within(primaryNav).getByRole('link', { name: /^My Place$/i })).toBeInTheDocument();
    expect(within(primaryNav).getByRole('link', { name: /^Festivals$/i })).toBeInTheDocument();
    expect(within(primaryNav).getByRole('link', { name: /^Best Time$/i })).toBeInTheDocument();
    expect(within(primaryNav).getByRole('link', { name: /^Birth Reading$/i })).toBeInTheDocument();

    await userEvent.click(within(primaryNav).getByRole('link', { name: /^Best Time$/i }));
    expect(await screen.findByRole('heading', { name: /Choose a date first/i }, routeLoadOptions)).toBeInTheDocument();
  }, 30000);

  it('keeps festivals and my-place inside the same product shell', async () => {
    setViewportWidth(1440);
    const festivalsRender = render(
      <MemoryRouter initialEntries={['/festivals']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Closest observances first/i }, routeLoadOptions)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /National/i })).toBeInTheDocument();
    festivalsRender.unmount();

    render(
      <MemoryRouter initialEntries={['/my-place']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Adjust the place only when the answer needs to change/i }, routeLoadOptions)).toBeInTheDocument();
    expect((await screen.findAllByText(/Morning Calm/i, {}, routeLoadOptions)).length).toBeGreaterThan(0);
  }, 30000);

  it('keeps the same shell on mobile widths and exposes the bottom navigation', async () => {
    setViewportWidth(390);
    render(
      <MemoryRouter initialEntries={['/today']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /The rest of today in one compact pass/i }, routeLoadOptions)).toBeInTheDocument();
    const bottomNav = document.querySelector('.app-shell__bottom-nav');
    expect(bottomNav).not.toBeNull();
    expect(within(bottomNav).getByText(/^Today$/i)).toBeInTheDocument();
    expect(within(bottomNav).getByText(/^My Place$/i)).toBeInTheDocument();
    expect(within(bottomNav).getByText(/^Festivals$/i)).toBeInTheDocument();
    expect(within(bottomNav).getByText(/^Best Time$/i)).toBeInTheDocument();
    expect(within(bottomNav).getByText(/^Birth Reading$/i)).toBeInTheDocument();
  }, 30000);

  it('closes the mobile dialog navigation on Escape', async () => {
    setViewportWidth(390);
    render(
      <MemoryRouter initialEntries={['/today']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /The rest of today in one compact pass/i }, routeLoadOptions)).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /^Menu$/i }));
    expect(screen.getByRole('dialog', { name: /Mobile menu/i })).toBeInTheDocument();

    await userEvent.keyboard('{Escape}');

    await waitFor(() => {
      expect(screen.queryByRole('dialog', { name: /Mobile menu/i })).not.toBeInTheDocument();
    });
  }, 30000);

  it('applies the selected UI language to document lang', async () => {
    setViewportWidth(390);
    window.localStorage.setItem('parva.temporal_context.v2', JSON.stringify({ language: 'ne' }));

    render(
      <MemoryRouter initialEntries={['/today']}>
        <App />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(document.documentElement.lang).toBe('ne');
    });
  }, 30000);

  it('preserves secondary routes and legacy redirects under the consumer shell', async () => {
    setViewportWidth(390);
    const firstRender = render(
      <MemoryRouter initialEntries={['/panchanga']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('button', { name: /How this was calculated/i }, routeLoadOptions)).toBeInTheDocument();
    expect(screen.getByText(/Secondary surface/i)).toBeInTheDocument();
    firstRender.unmount();

    render(
      <MemoryRouter initialEntries={['/muhurta']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Choose a date first/i }, routeLoadOptions)).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: /Primary/i })).toBeInTheDocument();
  }, 30000);
});
