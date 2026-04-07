import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { MuhurtaPage } from '../pages/MuhurtaPage';
import { TemporalProvider } from '../context/TemporalContext';

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

function buildCalendarPayload(type = 'general') {
  return {
    from: '2026-03-01',
    to: '2026-04-30',
    location: {
      latitude: 27.7172,
      longitude: 85.324,
      timezone: 'Asia/Kathmandu',
    },
    type,
    assumption_set_id: 'np-mainstream-v2',
    days: [
      {
        date: '2026-03-21',
        tone: 'strong',
        has_viable_window: true,
        top_score: type === 'travel' ? 72 : 92,
        window_count: 4,
        best_window: {
          name: type === 'travel' ? 'Departure window' : 'Abhijit Muhurta',
          start: '2026-03-21T10:30:00+05:45',
          end: '2026-03-21T12:15:00+05:45',
          rank_explanation: 'Clean opening with strong support.',
        },
      },
      {
        date: '2026-03-24',
        tone: 'good',
        has_viable_window: true,
        top_score: 80,
        window_count: 3,
        best_window: {
          name: 'Supportive window',
          start: '2026-03-24T09:15:00+05:45',
          end: '2026-03-24T10:45:00+05:45',
          rank_explanation: 'A strong backup date.',
        },
      },
    ],
    total: 2,
  };
}

function buildHeatmapEnvelope(date) {
  return {
    data: {
      date,
      location: {
        latitude: 27.7172,
        longitude: 85.324,
        timezone: 'Asia/Kathmandu',
      },
      type: 'general',
      assumption_set_id: 'np-mainstream-v2',
      best_window: {
        index: 1,
        name: date === '2026-03-24' ? 'Supportive window' : 'Abhijit Muhurta',
        start: `${date}T10:30:00+05:45`,
        end: `${date}T12:15:00+05:45`,
        class: 'auspicious',
        score: 88,
      },
      blocks: [
        {
          index: 1,
          name: date === '2026-03-24' ? 'Supportive window' : 'Abhijit Muhurta',
          start: `${date}T10:30:00+05:45`,
          end: `${date}T12:15:00+05:45`,
          class: 'auspicious',
          score: 88,
          reason_codes: ['quality:auspicious'],
        },
        {
          index: 2,
          name: 'Backup window',
          start: `${date}T14:00:00+05:45`,
          end: `${date}T15:15:00+05:45`,
          class: 'mixed',
          score: 54,
          reason_codes: ['quality:mixed'],
        },
      ],
      rahu_kalam: {
        start: `${date}T16:00:00+05:45`,
        end: `${date}T17:00:00+05:45`,
      },
      sunrise: `${date}T06:15:00+05:45`,
      sunset: `${date}T17:55:00+05:45`,
      ranking_profile: { minimum_score: 25 },
      tara_bala: { status: 'neutral' },
      calculation_trace_id: `trace-${date}`,
    },
    meta: {
      method: 'rule_ranked_muhurta_v2',
      confidence: { level: 'computed' },
    },
  };
}

describe('MuhurtaPage', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input, options) => {
        const url = String(input);
        if (url.includes('/muhurta/calendar?')) {
          const parsed = new URL(url, 'http://localhost');
          return response(buildCalendarPayload(parsed.searchParams.get('type') || 'general'));
        }
        if (url.includes('/muhurta/heatmap')) {
          const body = typeof options?.body === 'string' ? JSON.parse(options.body) : {};
          return response(buildHeatmapEnvelope(body.date || '2026-03-21'));
        }
        throw new Error(`Unexpected request: ${url}`);
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  function renderPage() {
    render(
      <MemoryRouter>
        <TemporalProvider>
          <MuhurtaPage />
        </TemporalProvider>
      </MemoryRouter>,
    );
  }

  it('renders ranked dates and updates day details when a new date is selected', async () => {
    renderPage();

    expect(await screen.findByRole('heading', { name: /Choose a date first/i })).toBeInTheDocument();
    expect(await screen.findByText(/Strongest dates/i)).toBeInTheDocument();
    expect(await screen.findByText(/Clean opening with strong support\./i)).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /Mar 24/i }));

    await waitFor(() => {
      expect(screen.getByText(/Tuesday, March 24, 2026/i)).toBeInTheDocument();
    });
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/muhurta/heatmap'),
      expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining('2026-03-24'),
      }),
    );
  }, 30000);

  it('reloads the planner when the activity changes', async () => {
    renderPage();

    expect(await screen.findByRole('heading', { name: /Choose a date first/i })).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Travel/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('type=travel'),
        expect.any(Object),
      );
    });
    expect(screen.getByRole('heading', { name: /Travel/i })).toBeInTheDocument();
  }, 15000);
});
