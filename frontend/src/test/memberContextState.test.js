import { createInitialMemberState, reducer, serializeMemberState } from '../context/memberContextState';

describe('member context state', () => {
  it('saves festivals directly in local guest-first mode', () => {
    const nextState = reducer(createInitialMemberState(), {
      type: 'saveFestival',
      payload: { id: 'dashain', name: 'Dashain' },
    });

    expect(nextState.savedFestivals).toEqual([
      { id: 'dashain', name: 'Dashain' },
    ]);
    expect(nextState.notice).toMatchObject({
      title: 'Observance saved',
    });
  });

  it('toggles reminders and updates the notice message', () => {
    const reminder = {
      id: 'festival:dashain',
      title: 'Dashain',
      kind: 'festival',
      date: '2026-10-20',
    };

    const added = reducer(createInitialMemberState(), {
      type: 'toggleReminder',
      payload: reminder,
    });

    expect(added.reminders).toEqual([reminder]);
    expect(added.notice).toMatchObject({
      title: 'Reminder added',
    });

    const removed = reducer(added, {
      type: 'toggleReminder',
      payload: reminder,
    });

    expect(removed.reminders).toEqual([]);
    expect(removed.notice).toMatchObject({
      title: 'Reminder removed',
    });
  });

  it('stores member reminder preferences', () => {
    const nextState = reducer(createInitialMemberState(), {
      type: 'updatePreferences',
      payload: {
        reminderChannel: 'off',
        reminderLeadTime: '3_days',
      },
    });

    expect(nextState.preferences).toMatchObject({
      reminderChannel: 'off',
      reminderLeadTime: '3_days',
    });
    expect(nextState.notice).toMatchObject({
      title: 'Preferences updated',
    });
  });

  it('imports local device data and normalizes older reminder channels', () => {
    const imported = reducer(createInitialMemberState(), {
      type: 'importLocalState',
      payload: {
        savedPlaces: [{ id: 'ktm', label: 'Kathmandu', timezone: 'Asia/Kathmandu' }],
        reminders: [{ id: 'festival:dashain', title: 'Dashain' }],
        preferences: {
          reminderChannel: 'email',
          reminderLeadTime: '1_week',
        },
      },
    });

    expect(imported.savedPlaces).toHaveLength(1);
    expect(imported.reminders).toHaveLength(1);
    expect(imported.preferences).toMatchObject({
      reminderChannel: 'in_app',
      reminderLeadTime: '1_week',
    });
    expect(imported.notice).toMatchObject({
      title: 'Local data imported',
    });
  });

  it('serializes and clears local device state', () => {
    const populated = reducer(createInitialMemberState(), {
      type: 'savePlace',
      payload: { id: 'ktm', label: 'Kathmandu', timezone: 'Asia/Kathmandu' },
    });

    const serialized = serializeMemberState(populated);
    expect(serialized).toMatchObject({
      savedPlaces: [{ id: 'ktm', label: 'Kathmandu', timezone: 'Asia/Kathmandu' }],
      preferences: {
        reminderChannel: 'in_app',
        reminderLeadTime: '1_day',
      },
    });

    const cleared = reducer(populated, { type: 'clearLocalState' });
    expect(cleared.savedPlaces).toEqual([]);
    expect(cleared.reminders).toEqual([]);
    expect(cleared.integrations).toEqual([]);
    expect(cleared.notice).toMatchObject({
      title: 'Local data cleared',
    });
  });
});
