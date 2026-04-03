export const MEMBER_STATE_SCHEMA_VERSION = 2;

export function createGuestAccount() {
  return {
    mode: 'guest',
    accountId: null,
    syncEnabled: false,
    profileVersion: 1,
    encryptionProfile: 'guest_cache',
    lastSyncedAt: null,
  };
}

export function createGuestPersistence() {
  return {
    store: 'guest_local',
    scope: 'device_cache',
    syncStatus: 'guest_ephemeral',
    localSaveEnabled: false,
    revision: 0,
    lastLoadedAt: null,
    lastPersistedAt: null,
    migratedFrom: null,
  };
}

function normalizeAccount(account, fallback = createGuestAccount()) {
  const next = {
    ...fallback,
    ...(account && typeof account === 'object' ? account : {}),
  };
  if (next.mode !== 'account') {
    next.mode = 'guest';
    next.accountId = null;
    next.syncEnabled = false;
  } else {
    next.syncEnabled = true;
  }
  return next;
}

function normalizePersistence(persistence, fallback = createGuestPersistence()) {
  const next = {
    ...fallback,
    ...(persistence && typeof persistence === 'object' ? persistence : {}),
  };
  next.revision = Number.isFinite(Number(next.revision)) ? Number(next.revision) : fallback.revision;
  next.localSaveEnabled = Boolean(next.localSaveEnabled);
  return next;
}

function placeKey(place = {}) {
  if (place.id) return place.id;
  return `${place.label || 'place'}:${place.latitude ?? ''}:${place.longitude ?? ''}:${place.timezone || ''}`;
}

function upsertBy(list = [], item, keyField = 'id') {
  const keyValue = item?.[keyField];
  if (!keyValue) return [...list, item];
  const next = list.filter((entry) => entry?.[keyField] !== keyValue);
  return [item, ...next];
}

function integrationKey(integration = {}) {
  if (integration.id) return integration.id;
  return integration.platform || integration.title || `integration:${Date.now()}`;
}

function upsertPlace(list = [], item) {
  const key = placeKey(item);
  const next = list.filter((entry) => placeKey(entry) !== key);
  return [{ ...item, id: key }, ...next];
}

function toggleById(list = [], item, keyField = 'id') {
  const keyValue = item?.[keyField];
  if (!keyValue) return list;
  if (list.some((entry) => entry?.[keyField] === keyValue)) {
    return list.filter((entry) => entry?.[keyField] !== keyValue);
  }
  return [item, ...list];
}

function removeById(list = [], id) {
  return list.filter((entry) => entry?.id !== id);
}

function normalizePreferences(preferences, fallback) {
  const next = {
    ...fallback,
    ...(preferences && typeof preferences === 'object' ? preferences : {}),
  };

  if (next.reminderChannel === 'email') {
    next.reminderChannel = 'in_app';
  }

  return next;
}

export function createInitialMemberState() {
  return {
    account: createGuestAccount(),
    persistence: createGuestPersistence(),
    notice: null,
    savedPlaces: [],
    savedFestivals: [],
    savedReadings: [],
    reminders: [],
    integrations: [],
    preferences: {
      reminderChannel: 'in_app',
      reminderLeadTime: '1_day',
      festivalAlerts: true,
      bestTimeAlerts: true,
      activityFocus: 'meditation',
      notificationStyle: 'balanced',
    },
  };
}

export function serializeMemberState(state) {
  const baseState = createInitialMemberState();
  return {
    account: normalizeAccount(state?.account, baseState.account),
    persistence: normalizePersistence(state?.persistence, baseState.persistence),
    savedPlaces: Array.isArray(state?.savedPlaces) ? state.savedPlaces : [],
    savedFestivals: Array.isArray(state?.savedFestivals) ? state.savedFestivals : [],
    savedReadings: Array.isArray(state?.savedReadings) ? state.savedReadings : [],
    reminders: Array.isArray(state?.reminders) ? state.reminders : [],
    integrations: Array.isArray(state?.integrations) ? state.integrations : [],
    preferences: normalizePreferences(state?.preferences, baseState.preferences),
  };
}

function buildNotice(kind, payload, options = {}) {
  switch (kind) {
    case 'savePlace':
      return {
        title: 'Place saved',
        body: `${payload?.label || 'Your place'} is now part of your guest-saved places on this device.`,
      };
    case 'saveFestival':
      return {
        title: 'Observance saved',
        body: `${payload?.name || 'This observance'} is now part of your guest-saved list on this device.`,
      };
    case 'saveReading':
      return {
        title: 'Reading saved',
        body: `${payload?.title || 'This birth reading'} is ready to revisit from your guest cache later.`,
      };
    case 'toggleReminder':
      return options.isActive
        ? {
            title: 'Reminder added',
            body: `${payload?.title || 'This reminder'} is now part of your guest reminder cache on this device.`,
          }
        : {
            title: 'Reminder removed',
            body: `${payload?.title || 'This reminder'} has been removed from your guest reminder cache.`,
          };
    case 'startIntegration':
      return {
        title: 'Integration saved',
        body: `${payload?.title || 'This calendar integration'} is now stored in your guest device cache.`,
      };
    case 'preferences':
      return {
        title: 'Preferences updated',
        body: 'Reminder preferences were updated for this guest device cache.',
      };
    case 'importLocalState':
      return {
        title: 'Device cache imported',
        body: 'Saved places, reminders, readings, and integrations were restored into this guest device cache.',
      };
    case 'clearLocalState':
      return {
        title: 'Device cache cleared',
        body: 'Saved items, reminders, integrations, and reminder preferences were cleared from this guest device cache.',
      };
    case 'setLocalSaveConsent':
      return payload?.enabled
        ? {
            title: 'Local save enabled',
            body: 'Saved places, reminders, and readings can now stay on this browser only until you purge them.',
          }
        : {
            title: 'Local save paused',
            body: 'Parva will stop writing personal data into this browser cache until you enable it again.',
          };
    default:
      return null;
  }
}

export function buildPersistenceFailureNotice() {
  return {
    title: 'Device cache unavailable',
    body: 'Parva could not update the guest device cache on this browser, so the latest change was not saved.',
  };
}

export function buildAccountSyncFailureNotice() {
  return {
    title: 'Account sync unavailable',
    body: 'Parva could not refresh the account-backed member state, so the last synced profile was kept in place.',
  };
}

export function reducer(state, action) {
  switch (action.type) {
    case 'hydrate':
      return {
        ...createInitialMemberState(),
        ...serializeMemberState(action.payload),
        notice: action.payload?.notice ?? null,
      };
    case 'savePlace':
      return {
        ...state,
        savedPlaces: upsertPlace(state.savedPlaces, action.payload),
        notice: buildNotice('savePlace', action.payload),
      };
    case 'saveFestival':
      return {
        ...state,
        savedFestivals: upsertBy(state.savedFestivals, action.payload),
        notice: buildNotice('saveFestival', action.payload),
      };
    case 'removeFestival':
      return {
        ...state,
        savedFestivals: removeById(state.savedFestivals, action.payload),
      };
    case 'saveReading':
      return {
        ...state,
        savedReadings: upsertBy(state.savedReadings, action.payload),
        notice: buildNotice('saveReading', action.payload),
      };
    case 'removeReading':
      return {
        ...state,
        savedReadings: removeById(state.savedReadings, action.payload),
      };
    case 'toggleReminder': {
      const isActive = !state.reminders.some((entry) => entry?.id === action.payload?.id);
      return {
        ...state,
        reminders: toggleById(state.reminders, action.payload),
        notice: buildNotice('toggleReminder', action.payload, { isActive }),
      };
    }
    case 'removeReminder':
      return {
        ...state,
        reminders: removeById(state.reminders, action.payload),
      };
    case 'removePlace':
      return {
        ...state,
        savedPlaces: removeById(state.savedPlaces, action.payload),
      };
    case 'startIntegration':
      return {
        ...state,
        integrations: upsertBy(state.integrations, action.payload, 'id'),
        notice: buildNotice('startIntegration', action.payload),
      };
    case 'removeIntegration':
      return {
        ...state,
        integrations: state.integrations.filter((entry) => {
          const key = integrationKey(entry);
          return key !== action.payload && entry?.platform !== action.payload;
        }),
      };
    case 'updatePreferences':
      return {
        ...state,
        preferences: normalizePreferences(action.payload, state.preferences),
        notice: buildNotice('preferences'),
      };
    case 'importLocalState':
      {
        const imported = serializeMemberState(action.payload);
        return {
          ...state,
          savedPlaces: imported.savedPlaces,
          savedFestivals: imported.savedFestivals,
          savedReadings: imported.savedReadings,
          reminders: imported.reminders,
          integrations: imported.integrations,
          preferences: imported.preferences,
          notice: buildNotice('importLocalState'),
        };
      }
    case 'clearLocalState': {
      const reset = createInitialMemberState();
      return {
        ...state,
        ...reset,
        account: state.account,
        persistence: {
          ...state.persistence,
          localSaveEnabled: false,
          syncStatus: 'guest_ephemeral',
        },
        notice: buildNotice('clearLocalState'),
      };
    }
    case 'setLocalSaveConsent':
      return {
        ...state,
        persistence: {
          ...state.persistence,
          localSaveEnabled: Boolean(action.payload?.enabled),
          syncStatus: action.payload?.enabled ? 'guest_cached' : 'guest_ephemeral',
        },
        notice: buildNotice('setLocalSaveConsent', action.payload),
      };
    case 'clearNotice':
      return {
        ...state,
        notice: null,
      };
    default:
      return state;
  }
}
