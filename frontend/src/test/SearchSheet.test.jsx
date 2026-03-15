import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { SearchSheet } from '../components/UI/SearchSheet';
import { MemberContext } from '../context/memberContextShared';

function LocationProbe() {
  const location = useLocation();
  return <p data-testid="location-probe">{location.pathname}</p>;
}

function renderSearch(memberState, onClose = vi.fn()) {
  return render(
    <MemberContext.Provider value={{ state: memberState }}>
      <MemoryRouter initialEntries={['/']}>
        <SearchSheet open onClose={onClose} />
        <LocationProbe />
      </MemoryRouter>
    </MemberContext.Provider>,
  );
}

describe('SearchSheet', () => {
  it('surfaces saved member items alongside page commands', async () => {
    const onClose = vi.fn();

    renderSearch({
      savedPlaces: [{ id: 'ktm', label: 'Kathmandu', timezone: 'Asia/Kathmandu' }],
      savedFestivals: [{ id: 'dashain', name: 'Dashain', category: 'national' }],
      savedReadings: [],
      reminders: [],
      integrations: [{ platform: 'google', title: 'Google Calendar' }],
    }, onClose);

    await userEvent.type(screen.getByRole('searchbox', { name: /Find a page or saved item/i }), 'dash');

    expect(screen.getByText('Saved observance')).toBeInTheDocument();
    const result = screen.getByRole('listitem');
    expect(result).toHaveTextContent('Dashain');

    await userEvent.click(result);

    expect(screen.getByTestId('location-probe')).toHaveTextContent('/festivals/dashain');
    expect(onClose).toHaveBeenCalled();
  });
});
