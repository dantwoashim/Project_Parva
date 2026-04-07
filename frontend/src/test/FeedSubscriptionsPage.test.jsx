import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { FeedSubscriptionsPage } from '../pages/FeedSubscriptionsPage';
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

describe('FeedSubscriptionsPage', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input) => {
        const url = String(input);
        if (url.includes('/festivals/coverage/scoreboard')) {
          return response({ data: { score: 100 }, meta: {} });
        }
        if (url.includes('/feeds/integrations/catalog')) {
          return response({
            generated_at: '2026-04-03',
            platforms: {
              apple: {
                title: 'Apple Calendar',
                badge: 'Best on iPhone, iPad, and Mac',
                cta_label: 'Open in Apple Calendar',
                copy_label: 'Copy Apple subscription link',
                steps: ['Tap Apple', 'Confirm subscription'],
              },
              google: {
                title: 'Google Calendar',
                badge: 'Desktop browser required',
                cta_label: 'Copy link and open Google Calendar',
                copy_label: 'Copy Google feed link',
                steps: ['Copy link', 'Paste in Google Calendar'],
              },
            },
            presets: [
              {
                key: 'all',
                title: 'All Festivals',
                description: 'The broadest Parva calendar, good for most personal use.',
                feed_url: 'https://example.com/v3/api/feeds/all.ics?years=2&lang=en',
                download_url: 'https://example.com/v3/api/feeds/all.ics?years=2&lang=en&download=1',
                platform_links: {
                  apple: {
                    open_url: 'webcal://example.com/v3/api/feeds/all.ics?years=2&lang=en',
                    copy_url: 'https://example.com/v3/api/feeds/all.ics?years=2&lang=en',
                    download_url: 'https://example.com/v3/api/feeds/all.ics?years=2&lang=en&download=1',
                  },
                  google: {
                    open_url: 'https://calendar.google.com/calendar/u/0/r/settings/addbyurl',
                    copy_url: 'https://example.com/v3/api/feeds/all.ics?years=2&lang=en',
                    download_url: 'https://example.com/v3/api/feeds/all.ics?years=2&lang=en&download=1',
                  },
                },
                stats: {
                  event_count: 42,
                  date_window: { start: '2026-01-01', end: '2027-12-30' },
                  next_event: { summary: 'Dashain', start_date: '2026-10-11', end_date: '2026-10-15' },
                  highlights: [{ summary: 'Dashain', start_date: '2026-10-11', end_date: '2026-10-15' }],
                },
              },
            ],
          });
        }
        if (url.includes('/feeds/integrations/custom-plan')) {
          return response({
            key: 'custom',
            title: 'Custom Calendar',
            description: 'Only the observances you selected, packaged for Apple Calendar, Google Calendar, and direct ICS use.',
            feed_url: 'https://example.com/v3/api/feeds/custom.ics?festivals=dashain&years=2&lang=en',
            download_url: 'https://example.com/v3/api/feeds/custom.ics?festivals=dashain&years=2&lang=en&download=1',
            selection_count: 1,
            festival_ids: ['dashain'],
            platform_links: {
              apple: {
                open_url: 'webcal://example.com/v3/api/feeds/custom.ics?festivals=dashain&years=2&lang=en',
                copy_url: 'https://example.com/v3/api/feeds/custom.ics?festivals=dashain&years=2&lang=en',
                download_url: 'https://example.com/v3/api/feeds/custom.ics?festivals=dashain&years=2&lang=en&download=1',
              },
              google: {
                open_url: 'https://calendar.google.com/calendar/u/0/r/settings/addbyurl',
                copy_url: 'https://example.com/v3/api/feeds/custom.ics?festivals=dashain&years=2&lang=en',
                download_url: 'https://example.com/v3/api/feeds/custom.ics?festivals=dashain&years=2&lang=en&download=1',
              },
            },
            stats: {
              event_count: 2,
              date_window: { start: '2026-10-11', end: '2027-10-01' },
              next_event: { summary: 'Dashain', start_date: '2026-10-11', end_date: '2026-10-15' },
              highlights: [{ summary: 'Dashain', start_date: '2026-10-11', end_date: '2026-10-15' }],
            },
          });
        }
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
      }),
    );

    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn(async () => {}),
      },
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('keeps raw feed urls hidden until the user opens advanced link details', async () => {
    render(
      <MemoryRouter>
        <MemberProvider>
          <FeedSubscriptionsPage />
        </MemberProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Connect Parva without dealing with raw calendar plumbing first/i })).toBeInTheDocument();
    expect(screen.queryByText(/\/v3\/api\/feeds\/all\.ics/i)).not.toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: /Copy link and open Google Calendar/i }).length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: /Open in Apple Calendar/i })).toBeInTheDocument();
    expect(screen.getByText(/42/)).toBeInTheDocument();
    expect(screen.getByText(/Next observance/i)).toBeInTheDocument();
    expect(screen.getByText(/No calendar connections yet/i)).toBeInTheDocument();

    await userEvent.click(screen.getByRole('checkbox', { name: /Dashain/i }));

    const selectedSummary = screen.getByText((_, element) => (
      element?.classList.contains('feeds-custom__summary') && element.textContent?.includes('Selected festivals')
    ));
    expect(selectedSummary).toHaveTextContent(/Selected festivals\s*1/);
    expect(await screen.findByText(/Custom feed ready/i)).toBeInTheDocument();
    expect(screen.queryByText(/\/v3\/api\/feeds\/custom\.ics/i)).not.toBeInTheDocument();

    await userEvent.click(screen.getByText(/^Advanced manual setup$/i));
    expect(screen.getByDisplayValue(/feeds\/custom\.ics/i)).toBeInTheDocument();
  }, 15000);
});
