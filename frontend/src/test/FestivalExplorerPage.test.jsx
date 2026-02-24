import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { FestivalExplorerPage } from '../pages/FestivalExplorerPage';
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

describe('FestivalExplorerPage', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input) => {
        const url = String(input);
        const hasHinduFilter = url.includes('category=hindu');

        return response({
          data: {
            groups: [
              {
                month_key: '2026-02',
                month_label: 'Falgun 2082',
                items: hasHinduFilter
                  ? [
                      {
                        id: 'shivaratri',
                        name: 'Maha Shivaratri',
                        display_name: 'Maha Shivaratri',
                        category: 'hindu',
                        start_date: '2026-02-15',
                        end_date: '2026-02-15',
                        quality_band: 'computed',
                      },
                    ]
                  : [
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
                        id: 'shivaratri',
                        name: 'Maha Shivaratri',
                        display_name: 'Maha Shivaratri',
                        category: 'hindu',
                        start_date: '2026-02-15',
                        end_date: '2026-02-15',
                        quality_band: 'computed',
                      },
                    ],
              },
            ],
            calculation_trace_id: 'tr_timeline_test',
          },
          meta: {},
        });
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('supports category filtering through API params', async () => {
    render(
      <MemoryRouter>
        <TemporalProvider>
          <FestivalExplorerPage />
        </TemporalProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Festival Explorer Ribbon/i })).toBeInTheDocument();
    expect(screen.getByText('Dashain')).toBeInTheDocument();

    await userEvent.selectOptions(screen.getByLabelText('Category'), 'hindu');

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('category=hindu'),
        expect.any(Object),
      );
    });

    expect(await screen.findByText('Maha Shivaratri')).toBeInTheDocument();
  });
});
