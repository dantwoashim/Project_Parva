import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { FestivalExplorerPage } from '../pages/FestivalExplorerPage';
import { TemporalProvider } from '../context/TemporalContext';
import { MemberProvider } from '../context/MemberContext';

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

describe('FestivalExplorerPage', () => {
  beforeEach(() => {
    window.innerWidth = 390;
    Element.prototype.scrollIntoView = vi.fn();

    vi.stubGlobal(
      'fetch',
      vi.fn(async (input) => {
        const url = String(input);
        const hasHinduFilter = url.includes('category=hindu');
        const hasLhosarSearch = url.includes('search=lhosar');

        if (url.includes('/festivals/on-date/')) {
          return response([
            {
              id: 'holi',
              name: 'Holi',
              tagline: 'Color and spring renewal are active today.',
              category: 'hindu',
              next_start: '2026-03-21',
              next_end: '2026-03-21',
            },
          ]);
        }

        return response({
          data: {
            groups: hasLhosarSearch
              ? []
              : [
                  {
                    month_key: '2026-03',
                    month_label: 'March 2026',
                    items: hasHinduFilter
                      ? [
                          {
                            id: 'shivaratri',
                            name: 'Maha Shivaratri',
                            display_name: 'Maha Shivaratri',
                            category: 'hindu',
                            start_date: '2026-03-28',
                            end_date: '2026-03-28',
                            quality_band: 'computed',
                            date_status: 'available',
                            date_status_note: 'Resolved calendar dates are available for this observance in the selected window.',
                          },
                        ]
                      : [
                          {
                            id: 'ghode-jatra',
                            name: 'Ghode Jatra',
                            display_name: 'Ghode Jatra',
                            category: 'regional',
                            start_date: '2026-03-24',
                            end_date: '2026-03-24',
                            quality_band: 'computed',
                            date_status: 'available',
                            date_status_note: 'Resolved calendar dates are available for this observance in the selected window.',
                          },
                          {
                            id: 'shivaratri',
                            name: 'Maha Shivaratri',
                            display_name: 'Maha Shivaratri',
                            category: 'hindu',
                            start_date: '2026-03-28',
                            end_date: '2026-03-28',
                            quality_band: 'computed',
                            date_status: 'available',
                            date_status_note: 'Resolved calendar dates are available for this observance in the selected window.',
                          },
                        ],
                  },
                ],
            calculation_trace_id: 'tr_timeline_test',
            facets: {
              categories: [{ value: 'hindu', label: 'Hindu', count: 1 }],
              months: [{ value: '2026-03', label: 'March 2026', count: 2 }],
              regions: [{ value: 'kathmandu-valley', label: 'Kathmandu Valley', count: 1 }],
            },
            unresolved_matches: hasLhosarSearch
              ? [
                  {
                    id: 'lhosar',
                    name: 'Lhosar',
                    display_name: 'Lhosar',
                    category: 'buddhist',
                    quality_band: 'inventory',
                    date_status: 'missing_rule',
                    date_status_note: 'No computed rule is published for this festival yet, so live dates cannot be resolved.',
                    summary: 'The search matched an observance that still needs a computed date rule.',
                  },
                ]
              : [],
          },
          meta: {},
        });
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
          <MemberProvider>
            <FestivalExplorerPage />
          </MemberProvider>
        </TemporalProvider>
      </MemoryRouter>,
    );
  }

  it('shows active-today observances before future dates in the closest section', async () => {
    renderPage();

    expect(
      await screen.findByRole('heading', {
        name: /Closest observances first/i,
      }),
    ).toBeInTheDocument();

    const closestSection = screen.getByText(/^Closest observances$/i).closest('section');
    const festivalHeadings = within(closestSection).getAllByRole('heading', { level: 3 });
    expect(festivalHeadings[0]).toHaveTextContent('Holi');
    expect(within(closestSection).getByText(/1 observance is active today/i)).toBeInTheDocument();
    expect(within(closestSection).getByRole('button', { name: /See all festivals/i })).toBeInTheDocument();
  }, 15000);

  it('supports category filtering through API params', async () => {
    renderPage();

    expect(
      await screen.findByRole('heading', {
        name: /Closest observances first/i,
      }),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Hindu' }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('category=hindu'),
        expect.any(Object),
      );
    });

    expect((await screen.findAllByText('Maha Shivaratri')).length).toBeGreaterThan(0);
  }, 15000);

  it('scrolls to all festivals and closes the filters dialog on Escape', async () => {
    renderPage();

    expect(
      await screen.findByRole('heading', {
        name: /Closest observances first/i,
      }),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /See all festivals/i }));
    expect(Element.prototype.scrollIntoView).toHaveBeenCalled();

    await userEvent.click(screen.getByRole('button', { name: /More filters/i }));
    expect(screen.getByRole('dialog', { name: /Refine the observance view/i })).toBeInTheDocument();

    await userEvent.keyboard('{Escape}');

    await waitFor(() => {
      expect(screen.queryByRole('dialog', { name: /Refine the observance view/i })).not.toBeInTheDocument();
    });
  }, 15000);

  it('surfaces unresolved search matches instead of pretending nothing matched', async () => {
    renderPage();

    expect(
      await screen.findByRole('heading', {
        name: /Closest observances first/i,
      }),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /More filters/i }));
    const dialog = screen.getByRole('dialog', { name: /Refine the observance view/i });
    fireEvent.change(within(dialog).getByRole('searchbox', { name: /Search/i }), {
      target: { value: 'lhosar' },
    });

    await waitFor(() => {
      expect(screen.getByText(/Still being verified/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/No computed rule is published/i)).toBeInTheDocument();
    expect(screen.getAllByText('Lhosar').length).toBeGreaterThan(0);
  }, 15000);
});
