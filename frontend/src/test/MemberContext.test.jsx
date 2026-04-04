import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemberProvider } from '../context/MemberContext';
import { createInitialMemberState } from '../context/memberContextState';
import { useMemberContext } from '../context/useMemberContext';

function MemberHarness() {
  const {
    state,
    toggleReminder,
    startIntegration,
  } = useMemberContext();

  return (
    <div>
      <button
        type="button"
        onClick={() => toggleReminder({
          id: 'festival:dashain',
          title: 'Dashain',
          kind: 'festival',
          date: '2026-10-20',
        })}
      >
        Toggle reminder
      </button>
      <button
        type="button"
        onClick={() => startIntegration({
          platform: 'google',
          title: 'Google Calendar',
          link: 'https://calendar.google.com/calendar/u/0/r',
          createdAt: '2026-03-20T09:00:00.000Z',
        })}
      >
        Start integration
      </button>
      <output>{`${state.reminders.length}:${state.integrations.length}`}</output>
      <p>{state.notice?.title || 'No notice'}</p>
    </div>
  );
}

describe('MemberProvider', () => {
  beforeEach(() => {
    window.parvaAnalytics = [];
  });

  it('records reminder and integration success events only after persistence succeeds', async () => {
    const store = {
      load: () => createInitialMemberState(),
      save: vi.fn(async (state) => ({
        ...state,
        persistence: {
          ...state.persistence,
          revision: (state.persistence?.revision || 0) + 1,
          store: 'guest_local',
          scope: 'device_cache',
        },
      })),
    };

    render(
      <MemberProvider store={store}>
        <MemberHarness />
      </MemberProvider>,
    );

    await userEvent.click(screen.getByRole('button', { name: /Toggle reminder/i }));
    await userEvent.click(screen.getByRole('button', { name: /Start integration/i }));

    await waitFor(() => {
      expect(store.save).toHaveBeenCalledTimes(2);
    });

    expect(window.parvaAnalytics.map((entry) => entry.event)).toEqual([
      'save_attempted',
      'reminder_created',
      'save_attempted',
      'calendar_integration_started',
    ]);
    expect(screen.getByText('1:1')).toBeInTheDocument();
  });

  it('does not emit reminder success analytics when the device cache write fails', async () => {
    const store = {
      load: () => createInitialMemberState(),
      save: vi.fn(async () => {
        throw new Error('storage failure');
      }),
    };

    render(
      <MemberProvider store={store}>
        <MemberHarness />
      </MemberProvider>,
    );

    await userEvent.click(screen.getByRole('button', { name: /Toggle reminder/i }));

    await waitFor(() => {
      expect(store.save).toHaveBeenCalledTimes(1);
    });

    expect(window.parvaAnalytics.map((entry) => entry.event)).toEqual([
      'save_attempted',
      'save_failed',
    ]);
    expect(screen.getByText('0:0')).toBeInTheDocument();
    expect(screen.getByText('Device cache unavailable')).toBeInTheDocument();
  });
});
