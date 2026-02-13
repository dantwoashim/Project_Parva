import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FeedSubscriptionsPage } from '../pages/FeedSubscriptionsPage';

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
            vi.fn(async () => response({
                data: {
                    festivals: [
                        { id: 'dashain', name: 'Dashain', category: 'national' },
                        { id: 'tihar', name: 'Tihar', category: 'national' },
                    ],
                    total: 2,
                },
                meta: {},
            })),
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

    it('builds custom iCal URL after festival selection', async () => {
        render(<FeedSubscriptionsPage />);

        expect(await screen.findByRole('heading', { name: /iCal Subscriptions/i })).toBeInTheDocument();

        await userEvent.click(screen.getByLabelText('Dashain'));

        const selectedSummary = screen.getByText((_, element) => {
            return element?.tagName === 'P' && element.textContent?.includes('Selected:');
        });
        expect(selectedSummary).toHaveTextContent('Selected: 1');
        expect(screen.getByText(/feeds\/custom\.ics/i)).toBeInTheDocument();
    });
});
