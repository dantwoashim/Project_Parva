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

  it('moves focus into the dialog and closes on Escape', async () => {
    const onClose = vi.fn();

    renderSearch({
      savedPlaces: [],
      savedFestivals: [],
      savedReadings: [],
      reminders: [],
      integrations: [],
    }, onClose);

    const searchbox = await screen.findByRole('searchbox', { name: /Find a page or saved item/i });
    expect(searchbox).toHaveFocus();

    await userEvent.keyboard('{Escape}');

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('keeps support surfaces out of the default command list until they are searched for', async () => {
    renderSearch({
      savedPlaces: [],
      savedFestivals: [],
      savedReadings: [],
      reminders: [],
      integrations: [],
    });

    expect(screen.getByText('Today')).toBeInTheDocument();
    expect(screen.queryByText('Integrations')).not.toBeInTheDocument();

    await userEvent.type(screen.getByRole('searchbox', { name: /Find a page or saved item/i }), 'integ');

    expect(screen.getByText('Integrations')).toBeInTheDocument();
    expect(screen.getByText('Beta page')).toBeInTheDocument();
  });
});
