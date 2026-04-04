import { fireEvent, render, screen } from '@testing-library/react';
import { FestivalDetail } from '../components/Festival/FestivalDetail';

describe('FestivalDetail ritual schema adapter', () => {
    it('renders ritual timeline when backend provides daily_rituals array', () => {
        const festival = {
            id: 'dashain',
            name: 'Dashain',
            category: 'national',
            calendar_type: 'lunar',
            duration_days: 10,
            daily_rituals: [
                {
                    day: 1,
                    name: 'Ghatasthapana',
                    description: 'The opening day ritual',
                    rituals: [
                        {
                            name: 'Kalash Setup',
                            description: 'Install sacred vessel',
                            time_of_day: 'Morning',
                            location: 'Home altar',
                        },
                    ],
                },
            ],
        };

        render(
            <FestivalDetail
                festival={festival}
                dates={{ start_date: '2026-10-20', end_date: '2026-10-30' }}
                onClose={() => {}}
                onLocationClick={() => {}}
                allFestivals={[]}
                onFestivalClick={() => {}}
            />,
        );

        fireEvent.click(screen.getByRole('tab', { name: /rituals/i }));

        expect(screen.getByText('Ghatasthapana')).toBeInTheDocument();
        expect(screen.getByText('Kalash Setup')).toBeInTheDocument();
    });
});
