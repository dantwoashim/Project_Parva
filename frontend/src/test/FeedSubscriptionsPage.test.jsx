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

    await userEvent.click(screen.getByRole('checkbox', { name: /Dashain/i }));

    const selectedSummary = screen.getByText((_, element) => (
      element?.classList.contains('feeds-custom__summary') && element.textContent?.includes('Selected festivals')
    ));
    expect(selectedSummary).toHaveTextContent(/Selected festivals\s*1/);
    expect(screen.queryByText(/\/v3\/api\/feeds\/custom\.ics/i)).not.toBeInTheDocument();

    await userEvent.click(screen.getAllByText(/Advanced manual setup/i)[3]);
    expect(screen.getByDisplayValue(/feeds\/custom\.ics/i)).toBeInTheDocument();
  });
});
