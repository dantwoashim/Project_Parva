import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { FestivalDetailPage } from '../pages/FestivalDetailPage';
import { MemberProvider } from '../context/MemberContext';
import { TemporalProvider } from '../context/TemporalContext';

function response(payload) {
  return {
    ok: true,
    status: 200,
    statusText: 'OK',
    json: async () => payload,
    text: async () => JSON.stringify(payload),
  };
}

describe('FestivalDetailPage', () => {
  beforeEach(() => {
    window.innerWidth = 390;
    window.innerHeight = 844;

    vi.stubGlobal(
      'fetch',
      vi.fn(async (input) => {
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
                category: 'national',
                calendar_type: 'lunar',
                duration_days: 10,
                description: 'Major Nepali festival.',
                ritual_sequence: {
                  days: [
                    {
                      name: 'Ghatasthapana',
                      events: [
                        {
                          title: 'Kalash Sthapana',
                          description: 'Sacred vessel installation',
                        },
                      ],
                    },
                  ],
                },
              },
              dates: { start_date: '2026-10-20', end_date: '2026-10-30' },
              completeness: {
                overall: 'complete',
                narrative: {
                  status: 'available',
                  note: 'Editorial origin, meaning, and contextual notes are published for this observance.',
                },
                ritual_sequence: {
                  status: 'available',
                  note: 'Structured ritual steps are published for this observance.',
                },
                dates: {
                  status: 'available',
                  note: 'Resolved calendar dates are available for the requested year.',
                },
                related_observances: {
                  status: 'missing',
                  note: 'No nearby observances were returned for this festival window.',
                },
              },
            },
            meta: { quality_band: 'computed', confidence: { level: 'high' } },
          });
        }
        if (url.includes('/festivals?')) {
          return response({
            data: {
              festivals: [{ id: 'dashain', name: 'Dashain', category: 'national' }],
              total: 1,
            },
            meta: {},
          });
        }
        if (url.includes('/temples/for-festival/')) {
          return response({ data: { temples: [] }, meta: {} });
        }
        return response({ data: {}, meta: {} });
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('loads festival details from route param and renders canonical ritual sequence', async () => {
    render(
      <MemoryRouter initialEntries={['/festivals/dashain']}>
        <TemporalProvider>
          <MemberProvider>
            <Routes>
              <Route path="/festivals/:festivalId" element={<FestivalDetailPage />} />
            </Routes>
          </MemberProvider>
        </TemporalProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: 'Dashain' })).toBeInTheDocument();
    expect(
      await screen.findByRole('heading', { name: /Open the evidence only when you want it\./i }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole('heading', { name: /The Ritual Timeline/i }),
    ).toBeInTheDocument();
    expect(await screen.findByText(/Kalash Sthapana/i)).toBeInTheDocument();
    expect(await screen.findByText(/Editorial origin, meaning, and contextual notes are published/i)).toBeInTheDocument();
  }, 15000);
});
