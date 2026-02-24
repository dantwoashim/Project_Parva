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

    if (url.includes('/temporal/compass?')) {
      return response({
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
          calculation_trace_id: 'tr_visual_compass',
        },
        meta: {
          confidence: { level: 'computed', score: 0.95 },
          trace_id: 'tr_visual_compass',
          method: 'ephemeris_udaya',
          provenance: { snapshot_id: 'snap_visual', dataset_hash: 'sha256:abc', rules_hash: 'sha256:def' },
          uncertainty: { boundary_risk: 'low', interval_hours: 0.5 },
          policy: { profile: 'np-mainstream', jurisdiction: 'NP', advisory: true },
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
                },
                {
                  id: 'tihar',
                  name: 'Tihar',
                  display_name: 'Tihar',
                  category: 'national',
                  start_date: '2026-11-07',
                  end_date: '2026-11-11',
                  quality_band: 'computed',
                },
              ],
            },
          ],
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
          provenance: { snapshot_id: 'snap_visual', dataset_hash: 'sha256:abc', rules_hash: 'sha256:def', verify_url: '/verify/tr_visual_panchanga' },
          uncertainty: { boundary_risk: 'low', interval_hours: 0.5 },
          policy: { profile: 'np-mainstream', jurisdiction: 'NP', advisory: true },
        },
      });
    }

    if (url.includes('/resolve?')) {
      return response({ data: { trace: { trace_id: 'tr_visual_resolve' } }, meta: {} });
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
          local_sunrise: '2026-02-15T06:44:00+05:45',
          sunrise: '2026-02-15T06:42:00+05:45',
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

    if (url.includes('/muhurta/heatmap?')) {
      return response({
        data: {
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
          ],
          best_window: {
            index: 6,
            name: 'Abhijit Muhurta',
            score: 88,
            confidence_score: 0.91,
            reason_codes: ['hora_supportive', 'tara_good'],
          },
          rahu_kalam: { segment: 8, start: '2026-02-15T16:12:00+05:45', end: '2026-02-15T17:00:00+05:45' },
          tara_bala: { quality: 'good', tara: { name: 'Sampat', distance: 2 } },
          rank_explanation: 'Ranked with hora/chaughadia/tara-bala constraints.',
          confidence_score: 0.9,
          calculation_trace_id: 'tr_muhurta_visual',
        },
        meta: {},
      });
    }

    if (url.includes('/kundali/graph?')) {
      return response({
        data: {
          layout: {
            houses: [
              { id: 'house_1', label: '1', x: 70, y: 70 },
              { id: 'house_7', label: '7', x: 250, y: 250 },
            ],
            grahas: [
              { id: 'mars', label: 'Mars', x: 120, y: 90, house_id: 'house_1' },
              { id: 'venus', label: 'Venus', x: 220, y: 210, house_id: 'house_7' },
            ],
            aspects: [{ id: 'asp_1', from: 'mars', to: 'venus', type: 'trine' }],
          },
          insight_blocks: [{ id: 'ins_1', title: 'Mars-Venus link', summary: 'Supportive trinal relation in this profile.' }],
          calculation_trace_id: 'tr_kundali_graph_visual',
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

async function renderRoute(route) {
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
    vi.spyOn(Date, 'now').mockReturnValue(new Date('2026-02-18T00:45:00Z').valueOf());
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('compass page visual baseline', async () => {
    const { container } = await renderRoute('/');
    await screen.findByRole('heading', { name: /Today's Festivals/i });
    expect(container.querySelector('.compass-page')).toMatchSnapshot();
  });

  it('explorer page visual baseline', async () => {
    const { container } = await renderRoute('/festivals');
    await screen.findByRole('heading', { name: /Festival Explorer Ribbon/i });
    expect(container.querySelector('.explorer-page')).toMatchSnapshot();
  });

  it('panchanga page visual baseline', async () => {
    const { container } = await renderRoute('/panchanga');
    await screen.findByText(/Confidence:/i);
    expect(container.querySelector('.panchanga-page')).toMatchSnapshot();
  });

  it('feeds page visual baseline', async () => {
    const { container } = await renderRoute('/feeds');
    await screen.findByRole('checkbox', { name: /Dashain/i });
    expect(container.querySelector('.feeds-page')).toMatchSnapshot();
  });

  it('personal page visual baseline', async () => {
    const { container } = await renderRoute('/personal');
    await screen.findByText(/Local sunrise delta vs Kathmandu baseline/i);
    expect(container.querySelector('.personal-page')).toMatchSnapshot();
  });

  it('muhurta page visual baseline', async () => {
    const { container } = await renderRoute('/muhurta');
    await screen.findByRole('heading', { name: /24h Muhurta Heatmap/i });
    expect(container.querySelector('.muhurta-page')).toMatchSnapshot();
  });

  it('kundali page visual baseline', async () => {
    const { container } = await renderRoute('/kundali');
    await screen.findByRole('heading', { name: /Interpretation Sidebar/i });
    expect(container.querySelector('.kundali-page')).toMatchSnapshot();
  });
});
