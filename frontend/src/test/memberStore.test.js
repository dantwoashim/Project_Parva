import { createInitialMemberState } from '../context/memberContextState';
import {
  MEMBER_LEGACY_STORAGE_KEYS,
  MEMBER_REMOTE_STORE_SCHEMA,
  MEMBER_STORE_SCHEMA,
  MEMBER_STORE_STORAGE_KEY,
  createLocalGuestMemberStore,
  createRemoteAccountMemberStore,
} from '../context/memberStore';

function createMemoryStorage(seed = {}) {
  const backing = new Map(Object.entries(seed));

  return {
    getItem: vi.fn((key) => (backing.has(key) ? backing.get(key) : null)),
    setItem: vi.fn((key, value) => {
      backing.set(key, String(value));
    }),
    removeItem: vi.fn((key) => {
      backing.delete(key);
    }),
    dump() {
      return Object.fromEntries(backing.entries());
    },
  };
}

describe('memberStore', () => {
  it('loads an empty guest device cache when browser storage is unavailable', () => {
    const store = createLocalGuestMemberStore({
      storage: null,
      now: () => '2026-03-20T09:00:00.000Z',
    });

    const state = store.load();

    expect(state.account).toEqual({
      mode: 'guest',
      accountId: null,
      syncEnabled: false,
      profileVersion: 1,
      encryptionProfile: 'guest_cache',
      lastSyncedAt: null,
    });
    expect(state.persistence).toMatchObject({
      store: 'guest_local',
      scope: 'device_cache',
      syncStatus: 'storage_unavailable',
      lastLoadedAt: '2026-03-20T09:00:00.000Z',
    });
  });

  it('migrates legacy guest cache state into the new device-cache model', () => {
    const legacyKey = MEMBER_LEGACY_STORAGE_KEYS[0];
    const storage = createMemoryStorage({
      [legacyKey]: JSON.stringify({
        savedFestivals: [{ id: 'dashain', name: 'Dashain' }],
        reminders: [{ id: 'festival:dashain', title: 'Dashain' }],
      }),
    });

    const store = createLocalGuestMemberStore({
      storage,
      now: () => '2026-03-20T09:15:00.000Z',
    });

    const state = store.load();

    expect(state.savedFestivals).toEqual([{ id: 'dashain', name: 'Dashain' }]);
    expect(state.reminders).toEqual([{ id: 'festival:dashain', title: 'Dashain' }]);
    expect(state.persistence).toMatchObject({
      migratedFrom: legacyKey,
      lastLoadedAt: '2026-03-20T09:15:00.000Z',
      scope: 'device_cache',
    });
  });

  it('persists a normalized envelope and clears legacy keys after save', async () => {
    const legacyKey = MEMBER_LEGACY_STORAGE_KEYS[0];
    const storage = createMemoryStorage({
      [legacyKey]: JSON.stringify({ reminders: [{ id: 'festival:old', title: 'Old reminder' }] }),
    });

    const store = createLocalGuestMemberStore({
      storage,
      now: () => '2026-03-20T09:30:00.000Z',
    });

    const saved = await store.save({
      ...createInitialMemberState(),
      notice: {
        title: 'Reminder added',
        body: 'Dashain is now part of your guest reminder cache on this device.',
      },
      reminders: [{ id: 'festival:dashain', title: 'Dashain' }],
      persistence: {
        revision: 2,
        lastLoadedAt: '2026-03-20T09:10:00.000Z',
        migratedFrom: legacyKey,
      },
    });

    const record = JSON.parse(storage.dump()[MEMBER_STORE_STORAGE_KEY]);

    expect(saved.notice).toMatchObject({
      title: 'Reminder added',
    });
    expect(saved.persistence).toMatchObject({
      revision: 3,
      lastLoadedAt: '2026-03-20T09:10:00.000Z',
      lastPersistedAt: '2026-03-20T09:30:00.000Z',
      scope: 'device_cache',
    });
    expect(record).toMatchObject({
      schema: MEMBER_STORE_SCHEMA,
      version: 2,
      storedAt: '2026-03-20T09:30:00.000Z',
      data: {
        reminders: [{ id: 'festival:dashain', title: 'Dashain' }],
        persistence: {
          revision: 3,
          lastPersistedAt: '2026-03-20T09:30:00.000Z',
        },
      },
    });
    expect(record.data.notice).toBeUndefined();
    expect(storage.removeItem).toHaveBeenCalledWith(legacyKey);
  });

  it('supports an account-backed remote member store contract', async () => {
    const transport = {
      loadMemberState: vi.fn(async () => ({
        ...createInitialMemberState(),
        account: {
          mode: 'account',
          accountId: 'acct_123',
        },
        savedFestivals: [{ id: 'dashain', name: 'Dashain' }],
      })),
      saveMemberState: vi.fn(async (state) => ({
        ...state,
        account: {
          mode: 'account',
          accountId: 'acct_123',
        },
      })),
    };

    const store = createRemoteAccountMemberStore({
      transport,
      account: {
        accountId: 'acct_123',
      },
      now: () => '2026-03-21T10:00:00.000Z',
    });

    expect(store.describe()).toEqual({
      kind: 'account_remote',
      scope: 'account',
      accountId: 'acct_123',
    });
    expect(MEMBER_REMOTE_STORE_SCHEMA).toBe('parva.member-store.account.v1');

    const loaded = store.load();
    expect(loaded.persistence).toMatchObject({
      store: 'account_remote',
      scope: 'account',
      syncStatus: 'sync_pending',
    });

    const hydrated = await store.hydrate();
    expect(hydrated.account).toMatchObject({
      mode: 'account',
      accountId: 'acct_123',
      syncEnabled: true,
      lastSyncedAt: '2026-03-21T10:00:00.000Z',
    });

    const saved = await store.save(hydrated, { reason: 'save_festival' });
    expect(saved.persistence).toMatchObject({
      store: 'account_remote',
      scope: 'account',
      syncStatus: 'synced',
      lastPersistedAt: '2026-03-21T10:00:00.000Z',
    });
    expect(transport.loadMemberState).toHaveBeenCalledTimes(1);
    expect(transport.saveMemberState).toHaveBeenCalledTimes(1);
  });
});
