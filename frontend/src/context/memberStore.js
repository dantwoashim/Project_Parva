import {
  MEMBER_STATE_SCHEMA_VERSION,
  createGuestAccount,
  createGuestPersistence,
  createInitialMemberState,
  serializeMemberState,
} from './memberContextState';

export const MEMBER_STORE_STORAGE_KEY = 'parva.member_context.v2';
export const MEMBER_LEGACY_STORAGE_KEYS = ['parva.member_context.v1'];
export const MEMBER_STORE_SCHEMA = 'parva.member-store.v2';
export const MEMBER_REMOTE_STORE_SCHEMA = 'parva.member-store.account.v1';

function resolveStorage(options = {}) {
  if (Object.prototype.hasOwnProperty.call(options, 'storage')) {
    return options.storage;
  }
  if (typeof window === 'undefined') return null;
  return window.localStorage ?? null;
}

function safeParse(rawValue) {
  if (typeof rawValue !== 'string' || !rawValue.trim()) return null;

  try {
    return JSON.parse(rawValue);
  } catch {
    return null;
  }
}

function nowIso(now) {
  const value = typeof now === 'function' ? now() : Date.now();
  return new Date(value).toISOString();
}

function normalizePersistedState(state, overrides = {}) {
  const normalized = serializeMemberState(state);
  const fallbackPersistence = createGuestPersistence();
  const currentPersistence = normalized.persistence || fallbackPersistence;
  const fallbackAccount = createGuestAccount();
  const currentAccount = normalized.account || fallbackAccount;
  const persistenceOverrides = overrides.persistence || overrides;
  const accountOverrides = overrides.account || {};

  return {
    ...createInitialMemberState(),
    ...normalized,
    notice: state?.notice ?? null,
    account: {
      ...fallbackAccount,
      ...currentAccount,
      ...accountOverrides,
    },
    persistence: {
      ...fallbackPersistence,
      ...currentPersistence,
      ...persistenceOverrides,
      store: persistenceOverrides.store || currentPersistence.store || fallbackPersistence.store,
      scope: persistenceOverrides.scope || currentPersistence.scope || fallbackPersistence.scope,
    },
  };
}

function buildStorageEnvelope(state, storedAt) {
  const persistedState = normalizePersistedState(state, {
    syncStatus: 'guest_cached',
    revision: Number(state?.persistence?.revision || 0) + 1,
    lastLoadedAt: state?.persistence?.lastLoadedAt || storedAt,
    lastPersistedAt: storedAt,
    migratedFrom: state?.persistence?.migratedFrom || null,
  });

  return {
    persistedState,
    envelope: {
      schema: MEMBER_STORE_SCHEMA,
      version: MEMBER_STATE_SCHEMA_VERSION,
      storedAt,
      data: serializeMemberState(persistedState),
    },
  };
}

function loadEnvelopeFromStorage(storage) {
  const currentRecord = safeParse(storage.getItem(MEMBER_STORE_STORAGE_KEY));
  if (currentRecord) {
    return {
      key: MEMBER_STORE_STORAGE_KEY,
      data: currentRecord?.schema === MEMBER_STORE_SCHEMA ? currentRecord.data : currentRecord,
    };
  }

  for (const legacyKey of MEMBER_LEGACY_STORAGE_KEYS) {
    const legacyRecord = safeParse(storage.getItem(legacyKey));
    if (legacyRecord) {
      return {
        key: legacyKey,
        data: legacyRecord?.data || legacyRecord,
      };
    }
  }

  return null;
}

export function createLocalGuestMemberStore(options = {}) {
  const storage = resolveStorage(options);
  const now = options.now;

  return {
    kind: 'guest_local',
    capabilities: {
      hydrated: false,
      synced: false,
    },
    describe() {
      return {
        kind: 'guest_local',
        scope: 'device_cache',
      };
    },
    load() {
      const loadedAt = nowIso(now);

      if (!storage || typeof storage.getItem !== 'function') {
        return normalizePersistedState(createInitialMemberState(), {
          syncStatus: 'storage_unavailable',
          lastLoadedAt: loadedAt,
        });
      }

      const loadedRecord = loadEnvelopeFromStorage(storage);
      if (!loadedRecord?.data) {
        return normalizePersistedState(createInitialMemberState(), {
          syncStatus: 'guest_cached',
          lastLoadedAt: loadedAt,
        });
      }

      return normalizePersistedState(loadedRecord.data, {
        syncStatus: 'guest_cached',
        lastLoadedAt: loadedAt,
        migratedFrom: loadedRecord.key === MEMBER_STORE_STORAGE_KEY ? null : loadedRecord.key,
      });
    },
    async save(state) {
      if (!storage || typeof storage.setItem !== 'function') {
        throw new Error('Guest device cache storage is unavailable.');
      }

      const storedAt = nowIso(now);
      const { persistedState, envelope } = buildStorageEnvelope(state, storedAt);
      storage.setItem(MEMBER_STORE_STORAGE_KEY, JSON.stringify(envelope));

      if (typeof storage.removeItem === 'function') {
        for (const legacyKey of MEMBER_LEGACY_STORAGE_KEYS) {
          storage.removeItem(legacyKey);
        }
      }

      return persistedState;
    },
  };
}


function normalizeRemoteAccount(account = {}) {
  return {
    ...createGuestAccount(),
    ...account,
    mode: 'account',
    syncEnabled: true,
    accountId: account.accountId || account.id || 'account',
    encryptionProfile: account.encryptionProfile || 'server_managed',
  };
}


function validateRemoteTransport(transport) {
  if (!transport || typeof transport.loadMemberState !== 'function' || typeof transport.saveMemberState !== 'function') {
    throw new Error('Remote account member store requires loadMemberState and saveMemberState transport methods.');
  }
}


export function createRemoteAccountMemberStore(options = {}) {
  const transport = options.transport;
  const now = options.now;
  const account = normalizeRemoteAccount(options.account);
  const bootstrapState = options.bootstrapState;
  validateRemoteTransport(transport);

  return {
    kind: 'account_remote',
    capabilities: {
      hydrated: true,
      synced: true,
    },
    describe() {
      return {
        kind: 'account_remote',
        scope: 'account',
        accountId: account.accountId,
      };
    },
    load() {
      return normalizePersistedState(bootstrapState || createInitialMemberState(), {
        account,
        persistence: {
          store: 'account_remote',
          scope: 'account',
          syncStatus: 'sync_pending',
          lastSyncedAt: bootstrapState?.account?.lastSyncedAt || null,
        },
      });
    },
    async hydrate() {
      const remoteState = await transport.loadMemberState({ account });
      const hydratedAt = nowIso(now);
      return normalizePersistedState(remoteState, {
        account: {
          ...account,
          lastSyncedAt: hydratedAt,
        },
        persistence: {
          store: 'account_remote',
          scope: 'account',
          syncStatus: 'synced',
          lastLoadedAt: hydratedAt,
          lastSyncedAt: hydratedAt,
        },
      });
    },
    async save(state, context = {}) {
      const remoteState = await transport.saveMemberState(serializeMemberState(state), {
        account,
        reason: context.reason || null,
        action: context.action || null,
      });
      const syncedAt = nowIso(now);
      return normalizePersistedState(remoteState, {
        account: {
          ...account,
          lastSyncedAt: syncedAt,
        },
        persistence: {
          store: 'account_remote',
          scope: 'account',
          syncStatus: 'synced',
          lastPersistedAt: syncedAt,
          lastSyncedAt: syncedAt,
        },
      });
    },
  };
}
