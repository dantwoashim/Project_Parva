import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
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

function buildFetchMock() {
  return vi.fn(async (...args) => {
    const [input] = args;
    const url = String(input);

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
                  summary: 'Blessing, reunion, and seasonal turning.',
                },
              ],
            },
          ],
          facets: {
            categories: [{ value: 'national', label: 'National', count: 1 }],
            months: [{ value: '2026-10', label: 'October', count: 1 }],
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
          bikram_sambat: { year: 2082, month_name: 'Falgun', day: 3 },
          primary_readout: { tithi_name: 'Chaturdashi', paksha: 'krishna' },
          today: { festivals: [{ id: 'dashain', name: 'Dashain' }] },
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
  let fetchMock;

  beforeEach(() => {
    window.innerWidth = 390;
    fetchMock = buildFetchMock();
    vi.stubGlobal('fetch', fetchMock);
    vi.stubGlobal('open', vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('drives festival search and filter state through the current explorer controls', async () => {
    render(
      <MemoryRouter initialEntries={['/festivals']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Closest observances first/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /More filters/i }));
    const filtersDialog = await screen.findByRole('dialog', { name: /Refine the observance view/i });

    fireEvent.change(within(filtersDialog).getByRole('searchbox', { name: /Search/i }), { target: { value: 'tihar' } });
    await waitFor(() => {
      expect(fetchMock.mock.calls.some(([url]) => String(url).includes('search=tihar'))).toBe(true);
    });

    await userEvent.click(screen.getByRole('button', { name: /National/i }));
    await waitFor(() => {
      expect(fetchMock.mock.calls.some(([url]) => String(url).includes('category=national'))).toBe(true);
    });
  }, 15000);

  it('updates best-time requests when the activity changes', async () => {
    render(
      <MemoryRouter initialEntries={['/best-time']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Choose a date first/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Travel' }));
    await waitFor(() => {
      const request = fetchMock.mock.calls.find(([url, options]) => String(url).includes('/muhurta/heatmap') && String(options?.body).includes('"type":"travel"'));
      expect(request).toBeTruthy();
    });
  }, 15000);

  it('navigates from a festival card into the detail page', async () => {
    render(
      <MemoryRouter initialEntries={['/festivals']}>
        <App />
      </MemoryRouter>,
    );

    const dashainLinks = await screen.findAllByRole('link', { name: /Dashain/i });
    await userEvent.click(dashainLinks[0]);

    expect(await screen.findByRole('heading', { name: 'Dashain' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /The Ritual Timeline/i })).toBeInTheDocument();
  }, 15000);

  it('shows place data and keeps profile as a secondary utility surface', async () => {
    render(
      <MemoryRouter initialEntries={['/profile']}>
        <App />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Keep preferences and device cache in one calm place/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Reminder behavior/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Export JSON/i })).toBeInTheDocument();
  }, 15000);
});
