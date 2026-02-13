import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { FestivalExplorerPage } from '../pages/FestivalExplorerPage';

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
                const hasSearch = url.includes('search=Shiva');
                const festivals = hasSearch
                    ? [{ id: 'shivaratri', name: 'Maha Shivaratri', category: 'hindu', duration_days: 1, next_occurrence: '2026-02-15' }]
                    : [
                        { id: 'dashain', name: 'Dashain', category: 'national', duration_days: 10, next_occurrence: '2026-10-20' },
                        { id: 'shivaratri', name: 'Maha Shivaratri', category: 'hindu', duration_days: 1, next_occurrence: '2026-02-15' },
                    ];

                return response({
                    data: {
                        festivals,
                        total: festivals.length,
                    },
                    meta: {},
                });
            }),
        );
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('supports search filtering through API params', async () => {
        render(
            <MemoryRouter>
                <FestivalExplorerPage />
            </MemoryRouter>,
        );

        expect(await screen.findByRole('heading', { name: /Festival Explorer/i })).toBeInTheDocument();
        expect(screen.getByText('Dashain')).toBeInTheDocument();

        await userEvent.type(screen.getByPlaceholderText(/Dashain, Tihar/i), 'Shiva');

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('search=Shiva'),
                expect.any(Object),
            );
        });

        expect(await screen.findByText('Maha Shivaratri')).toBeInTheDocument();
    });
});
