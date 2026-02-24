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

    if (url.includes('/temporal/compass?')) {
      return jsonResponse({
        data: {
          bikram_sambat: { year: 2082, month_name: 'Falgun', day: 3 },
          primary_readout: { tithi_name: 'Chaturdashi', paksha: 'krishna' },
          orbital: { phase_ratio: 0.74, tithi: 14 },
          horizon: {
            sunrise: '2026-02-15T06:42:00+05:45',
            sunset: '2026-02-15T17:53:00+05:45',
            current_muhurta: { name: 'Abhijit', class: 'auspicious' },
          },
          signals: {
            nakshatra: { name: 'Shravana' },
            yoga: { name: 'Shubha' },
            karana: { name: 'Vishti' },
            vaara: { name_english: 'Sunday' },
          },
          today: {
            festivals: [{ id: 'dashain', name: 'Dashain', start_date: '2026-10-20' }],
          },
          calculation_trace_id: 'tr_compass_routes',
        },
        meta: {},
      });
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
                  end_date: '2026-10-30',
                  quality_band: 'computed',
                },
              ],
            },
          ],
          calculation_trace_id: 'tr_timeline_routes',
        },
        meta: {},
      });
    }

    if (url.includes('/festivals/') && !url.includes('/festivals/timeline')) {
      return jsonResponse({
        data: {
          festival: {
            id: 'dashain',
            name: 'Dashain',
            category: 'national',
            duration_days: 10,
            description: 'Major Nepali festival.',
          },
          dates: { start_date: '2026-10-20', end_date: '2026-10-30' },
        },
        meta: {},
      });
    }

    if (url.includes('/festivals/on-date/')) {
      return jsonResponse({ data: [{ id: 'dashain', name: 'Dashain' }], meta: {} });
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

    if (url.includes('/personal/panchanga?')) {
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
          local_sunrise: '2026-02-12T06:44:00+05:45',
          sunrise: '2026-02-12T06:42:00+05:45',
          method_profile: 'personal_panchanga_v2_udaya',
          quality_band: 'gold',
          advisory_scope: 'ritual_planning',
          calculation_trace_id: 'tr_personal_routes_001',
        },
        meta: {},
      });
    }

    if (url.includes('/muhurta/heatmap?')) {
      return jsonResponse({
        data: {
          blocks: [
            {
              index: 6,
              name: 'Abhijit Muhurta',
              class: 'auspicious',
              score: 88,
              confidence_score: 0.91,
              reason_codes: ['hora_supportive', 'tara_good'],
            },
          ],
          best_window: {
            index: 6,
            name: 'Abhijit Muhurta',
            score: 88,
            confidence_score: 0.91,
            reason_codes: ['hora_supportive', 'tara_good'],
          },
          rahu_kalam: { segment: 7, start: '2026-02-15T13:36:00+05:45', end: '2026-02-15T15:00:00+05:45' },
          tara_bala: { quality: 'good', tara: { name: 'Sampat' } },
          rank_explanation: 'Filtered by hora/chaughadia/tara-bala.',
          confidence_score: 0.9,
          calculation_trace_id: 'tr_muhurta_routes',
        },
        meta: {},
      });
    }

    if (url.includes('/kundali/graph?')) {
      return jsonResponse({
        data: {
          layout: {
            houses: [{ id: 'house_1', label: '1', x: 60, y: 60 }],
            grahas: [{ id: 'mars', label: 'Mars', x: 140, y: 60, house_id: 'house_1' }],
            aspects: [{ id: 'asp_1', from: 'mars', to: 'house_1', type: 'trine' }],
          },
          insight_blocks: [{ id: 'ins_1', title: 'Mars in House 1', summary: 'Direct initiative signal.' }],
          calculation_trace_id: 'tr_kundali_graph_routes',
        },
        meta: {},
      });
    }

    if (url.includes('/kundali?')) {
      return jsonResponse({
        data: {
          lagna: { rashi_english: 'Pisces', rashi_sanskrit: 'Meena', longitude: 12.3 },
          grahas: {
            sun: { name_english: 'Sun', rashi_english: 'Aquarius', longitude: 332, dignity: { state: 'neutral' } },
            moon: { name_english: 'Moon', rashi_english: 'Capricorn', longitude: 288, dignity: { state: 'neutral' } },
          },
          houses: Array.from({ length: 12 }).map((_, index) => ({ house_number: index + 1, rashi_english: `House ${index + 1}`, occupants: [] })),
          aspects: [{ from: 'sun', to: 'moon', aspect_degree: 180, orb: 1, strength: 0.9 }],
          yogas: [{ id: 'gaja_kesari', description: 'Moon and Jupiter relation' }],
          doshas: [{ id: 'manglik', description: 'Mars influence marker' }],
          insight_blocks: [{ id: 'i1', title: 'Lagna context', summary: 'Pisces lagna baseline.' }],
          dasha: { total_major_periods: 9, timeline: [] },
          method_profile: 'kundali_v2_aspects_dasha',
          advisory_scope: 'astrology_assist',
        },
        meta: {},
      });
    }

    if (url.includes('/glossary?')) {
      return jsonResponse({
        data: {
          content: {
            title: 'Glossary',
            intro: 'Test glossary payload.',
            sections: [
              {
                id: 'core',
                title: 'Core',
                terms: [{ name: 'Tithi', meaning: 'Lunar day', why_it_matters: 'Determines observance timing.' }],
              },
            ],
          },
        },
        meta: {},
      });
    }

    if (url.includes('/feeds/next')) {
      return jsonResponse({ data: { events: [] }, meta: {} });
    }

    if (url.includes('/festivals?')) {
      return jsonResponse({ data: { festivals: [], total: 0 }, meta: {} });
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

  it('loads temporal compass by default and navigates to explorer and panchanga', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByText(/Temporal Compass/i)).toBeInTheDocument();

    await userEvent.click(screen.getByRole('link', { name: /Explorer/i }));
    expect(await screen.findByRole('heading', { name: /Festival Explorer Ribbon/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('link', { name: /Panchanga/i }));
    expect(await screen.findByText(/Confidence:/i)).toBeInTheDocument();
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

    expect(await screen.findByText(/Temporal Compass/i)).toBeInTheDocument();

    await userEvent.click(screen.getByRole('link', { name: /Personal/i }));
    expect(await screen.findByText(/Local sunrise delta vs Kathmandu baseline/i)).toBeInTheDocument();

    await userEvent.click(screen.getByRole('link', { name: /Muhurta/i }));
    expect(await screen.findByRole('heading', { name: /24h Muhurta Heatmap/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('link', { name: /Kundali/i }));
    expect(await screen.findByRole('heading', { name: /Interpretation Sidebar/i })).toBeInTheDocument();
  });
});
