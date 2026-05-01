import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

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

const festivalTimelineItems = [
  {
    id: 'dashain',
    name: 'Dashain',
    display_name: 'Dashain',
    category: 'national',
    start_date: '2026-10-20',
    end_date: '2026-10-30',
    bs_start: { formatted: '2083 Ashwin 4', month_name: 'Ashwin' },
    bs_end: { formatted: '2083 Ashwin 14', month_name: 'Ashwin' },
    duration_days: 10,
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
    bs_start: { formatted: '2083 Kartik 21', month_name: 'Kartik' },
    duration_days: 5,
    quality_band: 'computed',
    summary: 'Festival of lights with layered family and household observance.',
    regional_focus: ['Kathmandu Valley'],
  },
  {
    id: 'buddha-jayanti',
    name: 'Buddha Jayanti',
    display_name: 'Buddha Jayanti',
    category: 'buddhist',
    start_date: '2026-05-08',
    bs_start: { formatted: '2083 Baishakh 25', month_name: 'Baishakh' },
    quality_band: 'computed',
    summary: 'A full-moon Buddhist observance of refuge, dana, and lamps.',
    regional_focus: ['Lumbini'],
  },
  {
    id: 'chhath',
    name: 'Chhath Puja',
    display_name: 'Chhath Puja',
    category: 'regional',
    start_date: '2026-11-18',
    bs_start: { formatted: '2083 Mangsir 2', month_name: 'Mangsir' },
    quality_band: 'computed',
    summary: 'Solar vow observed with riverbank offerings and arghya.',
    regional_focus: ['Madhesh'],
  },
  {
    id: 'holi',
    name: 'Holi',
    display_name: 'Holi',
    category: 'seasonal',
    start_date: '2027-03-12',
    bs_start: { formatted: '2083 Falgun 29', month_name: 'Falgun' },
    quality_band: 'provisional',
    summary: 'A spring observance of color, release, and regional variation.',
    regional_focus: ['Nepal'],
  },
  {
    id: 'ekadashi-apara',
    name: 'Ekadashi (Apara)',
    display_name: 'Ekadashi (Apara)',
    category: 'fast',
    start_date: '2026-05-19',
    bs_start: { formatted: '2083 Jyestha 5', month_name: 'Jyestha' },
    quality_band: 'computed',
    summary: 'A Vishnu fast resolved from sunrise tithi and parana logic.',
    regional_focus: ['Nepal'],
  },
  {
    id: 'indra-jatra',
    name: 'Indra Jatra',
    display_name: 'Indra Jatra',
    category: 'regional',
    start_date: '2026-09-24',
    bs_start: { formatted: '2083 Ashwin 8', month_name: 'Ashwin' },
    quality_band: 'computed',
    summary: 'Kathmandu Valley jatra with chariot, mask, and community processions.',
    regional_focus: ['Kathmandu Valley'],
  },
];

function festivalTimelineEnvelope() {
  return {
    data: {
      groups: [
        {
          month_key: '2026-05',
          month_label: 'Baishakh/Jyestha 2083',
          items: festivalTimelineItems.filter((item) => ['buddha-jayanti', 'ekadashi-apara'].includes(item.id)),
        },
        {
          month_key: '2026-09',
          month_label: 'Ashwin 2083',
          items: festivalTimelineItems.filter((item) => ['indra-jatra', 'dashain'].includes(item.id)),
        },
        {
          month_key: '2026-11',
          month_label: 'Kartik/Mangsir 2083',
          items: festivalTimelineItems.filter((item) => ['tihar', 'chhath'].includes(item.id)),
        },
        {
          month_key: '2027-03',
          month_label: 'Falgun 2083',
          items: festivalTimelineItems.filter((item) => item.id === 'holi'),
        },
      ],
      facets: {
        categories: [
          { value: 'national', label: 'National', count: 2 },
          { value: 'regional', label: 'Regional', count: 2 },
          { value: 'buddhist', label: 'Buddhist', count: 1 },
          { value: 'fast', label: 'Fast / Vrata', count: 1 },
          { value: 'seasonal', label: 'Seasonal', count: 1 },
        ],
        months: [],
        regions: [
          { value: 'Nepal', label: 'Nepal', count: 4 },
          { value: 'Kathmandu Valley', label: 'Kathmandu Valley', count: 2 },
          { value: 'Madhesh', label: 'Madhesh', count: 1 },
        ],
      },
    },
    meta: {},
  };
}

function buildFetchMock() {
  return vi.fn(async (...args) => {
    const [input] = args;
    const url = String(input);

    if (url.includes('/festivals/timeline?')) {
      return jsonResponse(festivalTimelineEnvelope());
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
            category: 'national',
            description: 'Dashain gathers family, blessing, and renewal.',
            mythology: {
              summary: 'Renewal, protection, and blessing shape the festival story.',
              significance: 'The observance centers blessing, homecoming, and ritual continuity.',
            },
            ritual_sequence: {
              days: [{ name: 'Ghatasthapana', events: [{ title: 'Kalash Sthapana', description: 'Barley planting begins.' }] }],
            },
          },
          dates: {
            start_date: '2026-10-20',
            end_date: '2026-10-30',
            calculation_method: 'lunisolar festival profile',
          },
          nearby_festivals: [],
        },
        meta: {},
      });
    }

    if (url.includes('/muhurta/heatmap')) {
      return jsonResponse({
        data: {
          date: '2026-02-15',
          location: {
            latitude: 27.7172,
            longitude: 85.324,
            timezone: 'Asia/Kathmandu',
          },
          type: 'general',
          assumption_set_id: 'np-mainstream-v2',
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
          blocks: [
            {
              index: 6,
              name: 'Abhijit Muhurta',
              class: 'auspicious',
              score: 88,
              start: '2026-02-15T10:30:00+05:45',
              end: '2026-02-15T12:15:00+05:45',
            },
            {
              index: 7,
              name: 'Labh',
              class: 'mixed',
              score: 41,
              start: '2026-02-15T15:45:00+05:45',
              end: '2026-02-15T17:00:00+05:45',
            },
          ],
          best_window: {
            index: 6,
            name: 'Abhijit Muhurta',
            score: 88,
            start: '2026-02-15T10:30:00+05:45',
            end: '2026-02-15T12:15:00+05:45',
          },
          rahu_kalam: {
            start: '2026-02-15T13:15:00+05:45',
            end: '2026-02-15T14:30:00+05:45',
          },
        },
        meta: {},
      });
    }

    if (url.includes('/muhurta/calendar?')) {
      return jsonResponse({
        data: {
          from: '2026-04-01',
          to: '2026-05-31',
          type: 'general',
          location: {
            latitude: 27.7172,
            longitude: 85.324,
            timezone: 'Asia/Kathmandu',
          },
          assumption_set_id: 'np-mainstream-v2',
          days: [
            {
              date: '2026-04-04',
              tone: 'strong',
              window_count: 2,
              top_score: 88,
              has_viable_window: true,
              best_window: {
                name: 'Abhijit Muhurta',
                start: '2026-04-04T10:30:00+05:45',
                end: '2026-04-04T12:15:00+05:45',
                rank_explanation: 'This is the clearest opening in the current timing profile.',
                reason_codes: ['hora_supportive', 'tara_good'],
              },
            },
            {
              date: '2026-04-05',
              tone: 'good',
              window_count: 1,
              top_score: 62,
              has_viable_window: true,
              best_window: {
                name: 'Labh',
                start: '2026-04-05T15:45:00+05:45',
                end: '2026-04-05T17:00:00+05:45',
                rank_explanation: 'A reliable backup if you miss the main answer.',
                reason_codes: ['tara_good'],
              },
            },
          ],
        },
        meta: {},
      });
    }

    if (url.includes('/temporal/compass')) {
      return jsonResponse({
        data: {
          date: '2026-02-15',
          location: {
            latitude: 27.7172,
            longitude: 85.324,
            timezone: 'Asia/Kathmandu',
          },
          bikram_sambat: { year: 2082, month: 11, month_name: 'Falgun', day: 3 },
          primary_readout: { tithi_name: 'Chaturdashi', paksha: 'krishna' },
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
            },
          },
          signals: {
            nakshatra: { name: 'Shravana' },
            yoga: { name: 'Shubha' },
            karana: { name: 'Vishti' },
            vaara: { name_english: 'Sunday' },
          },
          today: { festivals: [{ id: 'dashain', name: 'Dashain' }], count: 1 },
          quality_band_filter: 'computed',
          engine: {
            method: 'ephemeris_udaya',
            method_profile: 'temporal_compass_v1',
          },
        },
        meta: {},
      });
    }

    if (url.includes('/festivals/upcoming?')) {
      return jsonResponse({ data: { festivals: [] }, meta: {} });
    }

    if (url.includes('/personal/context')) {
      return jsonResponse({
        data: {
          place_title: 'Kathmandu Home',
          visit_note: 'Saved locally on this device.',
          context_title: 'Morning Calm',
          context_summary: 'The place context stays calm and focused for the selected date.',
        },
        meta: {},
      });
    }

    if (url.includes('/personal/panchanga')) {
      return jsonResponse({
        data: {
          bikram_sambat: { year: 2082, month_name: 'Falgun', day: 3 },
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
        },
        meta: {},
      });
    }

    if (url.includes('/feeds/next')) {
      return jsonResponse({ data: { events: [] }, meta: {} });
    }

    if (url.includes('/glossary?')) {
      return jsonResponse({ data: { content: { title: 'Glossary', intro: '', sections: [] } }, meta: {} });
    }

    if (url.includes('/calendar/panchanga?')) {
      return jsonResponse({ data: {}, meta: {} });
    }

    return jsonResponse({ data: {}, meta: {} });
  });
}

describe('consumer route interactions', () => {
  beforeEach(() => {
    window.innerWidth = 390;
    window.localStorage.clear();
    vi.stubGlobal('fetch', buildFetchMock());
    vi.stubGlobal('open', vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    window.localStorage.clear();
  });

  it('renders the festivals surface as an API-backed expandable list', async () => {
    render(
      <MemoryRouter initialEntries={['/festivals']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /^Festivals$/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/7 festivals in this view/i)).toBeInTheDocument();
    expect(screen.queryByRole('dialog', { name: /Festival filters/i })).not.toBeInTheDocument();

    const dashainCard = screen.getByRole('button', { name: /Dashain/i });
    expect(dashainCard).toHaveAttribute('aria-expanded', 'false');
    await userEvent.click(dashainCard);
    expect(dashainCard).toHaveAttribute('aria-expanded', 'true');
    expect(await screen.findByText(/Mythology and Meaning/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Add to calendar/i })).toHaveAttribute('href', expect.stringContaining('festivals=dashain'));
    expect(screen.queryByRole('link', { name: /Open full page/i })).not.toBeInTheDocument();
  }, 15000);

  it('opens, applies, and resets the festival filter sheet', async () => {
    render(
      <MemoryRouter initialEntries={['/festivals']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /^Festivals$/i })).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Filters/i }));
    expect(screen.getByRole('dialog', { name: /Festival filters/i })).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /^Baishakh$/i }));
    await userEvent.click(screen.getByRole('button', { name: /Apply filters/i }));
    expect(screen.queryByRole('dialog', { name: /Festival filters/i })).not.toBeInTheDocument();
    expect(screen.getByLabelText(/1 festival in this view/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Buddha Jayanti/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /Filters/i }));
    await userEvent.click(screen.getByRole('button', { name: /^Reset$/i }));
    expect(screen.getByLabelText(/7 festivals in this view/i)).toBeInTheDocument();
  }, 15000);

  it('persists a followed festival into the saved workspace', async () => {
    render(
      <MemoryRouter initialEntries={['/festivals']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /^Festivals$/i })).toBeInTheDocument();
    const dashainArticle = screen.getByRole('button', { name: /Dashain/i }).closest('article');
    await userEvent.click(within(dashainArticle).getByRole('button', { name: /^Follow$/i }));
    expect(within(dashainArticle).getByRole('button', { name: /^Following$/i })).toBeInTheDocument();
    expect(window.localStorage.getItem('parva.savedFestivalIds.v1')).toContain('dashain');

    await userEvent.click(screen.getByRole('link', { name: /^Saved$/i }));
    expect(await screen.findByRole('heading', { name: /Profile & Saved/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^Dashain$/i })).toHaveAttribute('href', '/festivals/dashain');
    expect(screen.getByRole('link', { name: /^Calendar$/i })).toHaveAttribute('href', expect.stringContaining('festivals=dashain'));
  }, 15000);

  it('shows the interactive best-time surface', async () => {
    render(
      <MemoryRouter initialEntries={['/best-time']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /^Best Time$/i })).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /^Travel$/i }));
    const [abhijitWindow] = await screen.findAllByRole('button', { name: /Abhijit Muhurta/i });
    await userEvent.click(abhijitWindow);
    expect(screen.getByText(/Intent: Travel/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Copy time details/i })).toBeInTheDocument();
  }, 15000);

  it('opens and dismisses the search dialog', async () => {
    render(
      <MemoryRouter initialEntries={['/today']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Sunday, 2082 Falgun 3/i })).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Search Parva/i }));
    expect(screen.getByRole('dialog', { name: /Search Parva/i })).toBeInTheDocument();
    await userEvent.type(screen.getByPlaceholderText(/Search festivals/i), 'Dashain');
    expect(await screen.findByRole('link', { name: /Dashain/i })).toHaveAttribute('href', '/festivals/dashain');
    await userEvent.keyboard('{Escape}');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  }, 15000);

  it('keeps the festival detail route available for deep links', async () => {
    render(
      <MemoryRouter initialEntries={['/festivals/dashain']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /^Dashain$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Back to festivals/i })).toHaveAttribute('href', '/festivals');
  });

  it('shows the profile and saved-items surface', async () => {
    render(
      <MemoryRouter initialEntries={['/profile']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Profile & Saved/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Browse festivals/i })).toHaveAttribute('href', '/festivals');
  }, 15000);
});
