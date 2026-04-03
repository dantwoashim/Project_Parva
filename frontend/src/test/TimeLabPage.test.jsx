import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { TimeLabPage } from '../pages/TimeLabPage';
import { TemporalProvider } from '../context/TemporalContext';
import { STORAGE_KEY } from '../context/temporalContextState';

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

function createMemoryStorage() {
  const backing = new Map();

  return {
    getItem: vi.fn((key) => (backing.has(key) ? backing.get(key) : null)),
    setItem: vi.fn((key, value) => {
      backing.set(key, String(value));
    }),
    removeItem: vi.fn((key) => {
      backing.delete(key);
    }),
    clear: vi.fn(() => {
      backing.clear();
    }),
  };
}

function renderPage() {
  return render(
    <MemoryRouter>
      <TemporalProvider>
        <TimeLabPage />
      </TemporalProvider>
    </MemoryRouter>,
  );
}

describe('TimeLabPage', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'localStorage', {
      value: createMemoryStorage(),
      configurable: true,
    });

    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        date: '2026-04-14',
        timezone: 'Asia/Kathmandu',
      }),
    );

    vi.stubGlobal(
      'fetch',
      vi.fn(async (input, init) => {
        const url = String(input);

        if (url.includes('/calendar/convert/compare?date=')) {
          return response({
            match: true,
            official: '2083-01-01',
            estimated: '2083-01-01',
          });
        }

        if (url.includes('/calendar/convert?date=')) {
          return response({
            bikram_sambat: {
              year: 2083,
              month: 1,
              day: 1,
              month_name: 'Baisakh',
              confidence: 'official',
              source_range: 'official_lookup',
              estimated_error_days: 0,
            },
          });
        }

        if (url.includes('/calendar/bs-to-gregorian')) {
          expect(init?.method).toBe('POST');
          return response({
            gregorian: '2026-04-14',
            bs: {
              confidence: 'official',
              source_range: 'official_lookup',
              estimated_error_days: 0,
            },
          });
        }

        throw new Error(`Unhandled request in TimeLabPage test: ${url}`);
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('uses the live engine for source-backed BS to AD conversion', async () => {
    renderPage();

    expect(await screen.findByRole('heading', { name: /Infinite Conversion Lab/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /2083 BS/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/calendar/bs-to-gregorian'),
        expect.objectContaining({ method: 'POST' }),
      );
    });

    expect(screen.getByText(/Live engine answer/i)).toBeInTheDocument();
    expect(screen.getByText(/Source range: official_lookup/i)).toBeInTheDocument();
    expect(screen.getByText(/Live answer with projected mirror/i)).toBeInTheDocument();
    expect(screen.getAllByText(/April 14, .*AD/i).length).toBeGreaterThan(0);
  }, 10000);

  it('stays explicit about projected mode for deep-time jumps', async () => {
    renderPage();

    expect(await screen.findByRole('heading', { name: /Infinite Conversion Lab/i })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /10,000 BC/i }));

    expect(await screen.findByText(/Live engine unavailable/i)).toBeInTheDocument();
    expect(screen.getByText(/Projected mirror only/i)).toBeInTheDocument();
    expect(screen.getByText(/Projected deep-time mode/i)).toBeInTheDocument();
    expect(screen.getAllByText(/10,000 BC/i).length).toBeGreaterThan(0);
  });
});
