import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

function jsonResponse(payload) {
    return {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => payload,
        text: async () => JSON.stringify(payload),
    };
}

function buildFetchMock() {
    return vi.fn(async (input) => {
        const url = String(input);

        if (url.includes('/festivals') && !url.includes('/festivals/')) {
            return jsonResponse({
                data: {
                    festivals: [
                        {
                            id: 'dashain',
                            name: 'Dashain',
                            category: 'national',
                            duration_days: 10,
                            next_occurrence: '2026-10-20',
                        },
                    ],
                    total: 1,
                },
                meta: {},
            });
        }

        if (url.includes('/calendar/panchanga')) {
            return jsonResponse({
                data: {
                    date: '2026-02-12',
                    bikram_sambat: { year: 2082, month: 10, day: 30, month_name: 'Magh' },
                    panchanga: {
                        confidence: 'astronomical',
                        tithi: { number: 10, name: 'Dashami', paksha: 'shukla', method: 'ephemeris_udaya', sunrise_used: '2026-02-12T06:45:00+05:45' },
                        nakshatra: { name: 'Rohini', pada: 2 },
                        yoga: { name: 'Siddha', number: 1 },
                        karana: { name: 'Bava', number: 1 },
                        vaara: { name_english: 'Thursday', name_sanskrit: 'Guruvara' },
                    },
                    ephemeris: { mode: 'swiss_moshier' },
                },
                meta: {},
            });
        }

        if (url.includes('/feeds/next')) {
            return jsonResponse({ data: { events: [] }, meta: {} });
        }

        return jsonResponse({ data: {}, meta: {} });
    });
}

describe('App routing', () => {
    beforeEach(() => {
        vi.stubGlobal('fetch', buildFetchMock());
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('loads explorer by default and navigates to panchanga page', async () => {
        render(
            <MemoryRouter initialEntries={['/']}>
                <App />
            </MemoryRouter>,
        );

        expect(await screen.findByRole('heading', { name: /Festival Explorer/i })).toBeInTheDocument();

        await userEvent.click(screen.getByRole('link', { name: /Panchanga/i }));

        expect(await screen.findByRole('heading', { name: /Panchanga Viewer/i })).toBeInTheDocument();
        expect(await screen.findByRole('heading', { name: /Panchanga Response Authority/i })).toBeInTheDocument();
        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/calendar/panchanga?date='),
                expect.any(Object),
            );
        });
    });
});
