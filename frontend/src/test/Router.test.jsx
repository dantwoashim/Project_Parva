import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  BrowserRouter,
  Link,
  MemoryRouter,
  Navigate,
  NavLink,
  Route,
  Routes,
  useLocation,
  useParams,
} from '@parva/router';

function LocationProbe() {
  const location = useLocation();
  return <output aria-label="Current path">{`${location.pathname}${location.search}`}</output>;
}

function FestivalProbe() {
  const { festivalId } = useParams();
  return <h1>{festivalId}</h1>;
}

describe('Parva router', () => {
  test('matches dynamic route parameters', () => {
    render(
      <MemoryRouter initialEntries={['/festivals/dashain']}>
        <Routes>
          <Route path="/festivals/:festivalId" element={<FestivalProbe />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole('heading', { name: 'dashain' })).toBeInTheDocument();
  });

  test('moves between internal links without reloading the document', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={['/']}>
        <Link to="/today?source=home">Open today</Link>
        <LocationProbe />
      </MemoryRouter>,
    );

    await user.click(screen.getByRole('link', { name: 'Open today' }));
    expect(screen.getByLabelText('Current path')).toHaveTextContent('/today?source=home');
  });

  test('marks the active navigation link', () => {
    render(
      <MemoryRouter initialEntries={['/trust/method']}>
        <NavLink to="/trust" className={({ isActive }) => (isActive ? 'is-active' : '')}>
          Trust
        </NavLink>
      </MemoryRouter>,
    );

    expect(screen.getByRole('link', { name: 'Trust' })).toHaveClass('is-active');
    expect(screen.getByRole('link', { name: 'Trust' })).toHaveAttribute('aria-current', 'page');
  });

  test('handles declarative redirects', async () => {
    render(
      <MemoryRouter initialEntries={['/legacy']}>
        <Routes>
          <Route path="/legacy" element={<Navigate to="/today" replace />} />
          <Route path="/today" element={<h1>Today</h1>} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: 'Today' })).toBeInTheDocument();
  });

  test('updates browser history for client-side navigation', async () => {
    const user = userEvent.setup();
    window.history.replaceState(null, '', '/');

    render(
      <BrowserRouter>
        <Link to="/panchanga">Panchanga</Link>
        <LocationProbe />
      </BrowserRouter>,
    );

    await user.click(screen.getByRole('link', { name: 'Panchanga' }));
    expect(window.location.pathname).toBe('/panchanga');
    expect(screen.getByLabelText('Current path')).toHaveTextContent('/panchanga');
  });
});
