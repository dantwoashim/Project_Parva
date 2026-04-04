import {
  createGuestPersistence,
  createInitialMemberState,
  reducer,
  serializeMemberState,
} from '../context/memberContextState';

describe('member context state', () => {
  it('saves festivals in guest device-cache mode', () => {
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

  it('updates local-save consent and sync posture explicitly', () => {
    const enabled = reducer(createInitialMemberState(), {
      type: 'setLocalSaveConsent',
      payload: { enabled: true },
    });

    expect(enabled.persistence).toMatchObject({
      localSaveEnabled: true,
      syncStatus: 'guest_cached',
    });
    expect(enabled.notice).toMatchObject({
      title: 'Local save enabled',
    });

    const disabled = reducer(enabled, {
      type: 'setLocalSaveConsent',
      payload: { enabled: false },
    });

    expect(disabled.persistence).toMatchObject({
      localSaveEnabled: false,
      syncStatus: 'guest_ephemeral',
    });
    expect(disabled.notice).toMatchObject({
      title: 'Local save paused',
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
      title: 'Device cache imported',
    });
  });

  it('serializes guest account metadata and clears only cached data', () => {
    const populated = reducer({
      ...createInitialMemberState(),
      account: {
        mode: 'account',
        accountId: 'member-123',
      },
      persistence: {
        ...createGuestPersistence(),
        revision: 4,
      },
    }, {
      type: 'savePlace',
      payload: { id: 'ktm', label: 'Kathmandu', timezone: 'Asia/Kathmandu' },
    });

    const serialized = serializeMemberState(populated);
    expect(serialized).toMatchObject({
      account: {
        mode: 'account',
        accountId: 'member-123',
      },
      persistence: {
        store: 'guest_local',
        scope: 'device_cache',
        localSaveEnabled: false,
        revision: 4,
      },
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
    expect(cleared.account).toEqual({
      mode: 'account',
      accountId: 'member-123',
    });
    expect(cleared.persistence).toMatchObject({
      localSaveEnabled: false,
      revision: 4,
      scope: 'device_cache',
    });
    expect(cleared.notice).toMatchObject({
      title: 'Device cache cleared',
    });
  });

  it('imports cache data without replacing the active account or persistence metadata', () => {
    const currentState = {
      ...createInitialMemberState(),
      account: {
        mode: 'account',
        accountId: 'member-123',
      },
      persistence: {
        ...createGuestPersistence(),
        revision: 7,
        lastPersistedAt: '2026-03-20T10:00:00.000Z',
      },
    };

    const imported = reducer(currentState, {
      type: 'importLocalState',
      payload: {
        account: {
          mode: 'guest',
        },
        persistence: {
          revision: 1,
        },
        reminders: [{ id: 'festival:holi', title: 'Holi' }],
      },
    });

    expect(imported.account).toEqual(currentState.account);
    expect(imported.persistence).toEqual(currentState.persistence);
    expect(imported.reminders).toEqual([{ id: 'festival:holi', title: 'Holi' }]);
    expect(imported.notice).toMatchObject({
      title: 'Device cache imported',
    });
  });

  it('keeps multiple integrations when they have distinct ids and removes by id cleanly', () => {
    const withGooglePreset = reducer(createInitialMemberState(), {
      type: 'startIntegration',
      payload: {
        id: 'google-all',
        platform: 'google',
        title: 'All Festivals for Google Calendar',
      },
    });

    const withGoogleCustom = reducer(withGooglePreset, {
      type: 'startIntegration',
      payload: {
        id: 'google-custom-dashain',
        platform: 'google-custom',
        title: 'Dashain for Google Calendar',
      },
    });

    expect(withGoogleCustom.integrations).toHaveLength(2);

    const removed = reducer(withGoogleCustom, {
      type: 'removeIntegration',
      payload: 'google-all',
    });

    expect(removed.integrations).toHaveLength(1);
    expect(removed.integrations[0]).toMatchObject({
      id: 'google-custom-dashain',
    });
  });
});
