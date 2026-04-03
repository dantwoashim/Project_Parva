import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { SearchSheet } from '../components/UI/SearchSheet';
import { MemberContext } from '../context/memberContextShared';
import { TemporalContext } from '../context/temporalContextShared';

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

function LocationProbe() {
  const location = useLocation();
  return <p data-testid="location-probe">{location.pathname}</p>;
}

function renderSearch({
  memberState,
  temporalState = {
    date: '2026-04-14',
    timezone: 'Asia/Kathmandu',
    language: 'en',
    location: { latitude: 27.7172, longitude: 85.324 },
  },
  onClose = vi.fn(),
} = {}) {
  const setLocation = vi.fn();
  const setTimezone = vi.fn();

  const view = render(
    <TemporalContext.Provider value={{ state: temporalState, setLocation, setTimezone }}>
      <MemberContext.Provider value={{ state: memberState }}>
        <MemoryRouter initialEntries={['/']}>
          <SearchSheet open onClose={onClose} />
          <LocationProbe />
        </MemoryRouter>
      </MemberContext.Provider>
    </TemporalContext.Provider>,
  );

  return { ...view, setLocation, setTimezone, onClose };
}

describe('SearchSheet', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input) => {
        const url = String(input);

        if (url.includes('/festivals/timeline')) {
          return response({
            data: {
              groups: [
                {
                  month_key: '2026-10',
                  month_label: 'October 2026',
                  items: [
                    {
                      id: 'dashain',
                      name: 'Dashain',
                      display_name: 'Dashain',
                      category: 'national',
                      start_date: '2026-10-20',
                      end_date: '2026-10-20',
                      summary: 'Nepal’s major autumn festival.',
                    },
                  ],
                },
              ],
            },
            meta: {
              confidence: { level: 'computed' },
              method: 'festival_timeline',
              provenance: {},
              uncertainty: { boundary_risk: 'low', interval_hours: null },
              degraded: { active: false, reasons: [], defaults_applied: [] },
            },
          });
        }

        if (url.includes('/places/search')) {
          return response({
            items: [
              {
                label: 'Kathmandu',
                latitude: 27.7172,
                longitude: 85.324,
                timezone: 'Asia/Kathmandu',
                source: 'offline_nepal_gazetteer_search',
              },
            ],
          });
        }

        throw new Error(`Unhandled request in SearchSheet test: ${url}`);
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('surfaces glossary meanings alongside pages and saved items', async () => {
    renderSearch({
      memberState: {
        savedPlaces: [],
        savedFestivals: [],
        savedReadings: [],
        reminders: [],
        integrations: [],
      },
    });

    fireEvent.change(screen.getByRole('searchbox', { name: /Find a page, place, festival, or meaning/i }), {
      target: { value: 'panchami' },
    });

    await waitFor(() => {
      expect(screen.getByText('Glossary term')).toBeInTheDocument();
      expect(screen.getByText('Panchami')).toBeInTheDocument();
    });
  });

  it('moves focus into the dialog and closes on Escape', async () => {
    const { onClose } = renderSearch({
      memberState: {
        savedPlaces: [],
        savedFestivals: [],
        savedReadings: [],
        reminders: [],
        integrations: [],
      },
    });

    const searchbox = await screen.findByRole('searchbox', { name: /Find a page, place, festival, or meaning/i });
    expect(searchbox).toHaveFocus();

    await userEvent.keyboard('{Escape}');

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('keeps support surfaces out of the default command list until they are searched for', async () => {
    renderSearch({
      memberState: {
        savedPlaces: [],
        savedFestivals: [],
        savedReadings: [],
        reminders: [],
        integrations: [],
      },
    });

    expect(screen.getByText('Today')).toBeInTheDocument();
    expect(screen.queryByText('Integrations')).not.toBeInTheDocument();

    fireEvent.change(screen.getByRole('searchbox', { name: /Find a page, place, festival, or meaning/i }), {
      target: { value: 'integ' },
    });

    await waitFor(() => {
      expect(screen.getByText('Integrations')).toBeInTheDocument();
    });
    expect(screen.getByText('Beta page')).toBeInTheDocument();
  });
});
