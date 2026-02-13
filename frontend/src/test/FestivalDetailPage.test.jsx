import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { FestivalDetailPage } from '../pages/FestivalDetailPage';

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
        vi.stubGlobal(
            'fetch',
            vi.fn(async (input) => {
                const url = String(input);
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
                            },
                            dates: { start_date: '2026-10-20', end_date: '2026-10-30' },
                        },
                        meta: {},
                    });
                }
                if (url.includes('/festivals')) {
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

    it('loads festival details from route param', async () => {
        render(
            <MemoryRouter initialEntries={['/festivals/dashain']}>
                <Routes>
                    <Route path="/festivals/:festivalId" element={<FestivalDetailPage />} />
                </Routes>
            </MemoryRouter>,
        );

        expect(await screen.findByRole('heading', { name: 'Dashain' })).toBeInTheDocument();
        expect(await screen.findByRole('heading', { name: /Festival Response Authority/i })).toBeInTheDocument();
    });
});
