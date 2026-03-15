export const MEMBER_STORAGE_KEY = 'parva.member_context.v1';

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

export function serializeMemberState(state) {
  return {
    savedPlaces: Array.isArray(state?.savedPlaces) ? state.savedPlaces : [],
    savedFestivals: Array.isArray(state?.savedFestivals) ? state.savedFestivals : [],
    savedReadings: Array.isArray(state?.savedReadings) ? state.savedReadings : [],
    reminders: Array.isArray(state?.reminders) ? state.reminders : [],
    integrations: Array.isArray(state?.integrations) ? state.integrations : [],
    preferences: normalizePreferences(state?.preferences, createInitialMemberState().preferences),
  };
}

function buildNotice(kind, payload, options = {}) {
  switch (kind) {
    case 'savePlace':
      return {
        title: 'Place saved',
        body: `${payload?.label || 'Your place'} is now part of your saved places.`,
      };
    case 'saveFestival':
      return {
        title: 'Observance saved',
        body: `${payload?.name || 'This observance'} is now waiting in Saved.`,
      };
    case 'saveReading':
      return {
        title: 'Reading saved',
        body: `${payload?.title || 'This birth reading'} is ready to revisit later.`,
      };
    case 'toggleReminder':
      return options.isActive
        ? {
            title: 'Reminder added',
            body: `${payload?.title || 'This reminder'} is now part of your local reminder list on this device.`,
          }
        : {
            title: 'Reminder removed',
            body: `${payload?.title || 'This reminder'} has been removed from your saved reminders.`,
          };
    case 'startIntegration':
      return {
        title: 'Integration saved',
        body: `${payload?.title || 'This calendar integration'} is now kept in your local saved state.`,
      };
    case 'preferences':
      return {
        title: 'Preferences updated',
        body: 'Reminder preferences were updated for this local profile.',
      };
    case 'importLocalState':
      return {
        title: 'Local data imported',
        body: 'Saved places, reminders, readings, and integrations were restored on this device.',
      };
    case 'clearLocalState':
      return {
        title: 'Local data cleared',
        body: 'Saved items, reminders, integrations, and reminder preferences were cleared from this device.',
      };
    default:
      return null;
  }
}

export function createInitialMemberState() {
  return {
    notice: null,
    savedPlaces: [],
    savedFestivals: [],
    savedReadings: [],
    reminders: [],
    integrations: [],
    preferences: {
      reminderChannel: 'in_app',
      reminderLeadTime: '1_day',
    },
  };
}

export function loadInitialMemberState() {
  const baseState = createInitialMemberState();

  if (
    typeof localStorage === 'undefined'
    || typeof localStorage.getItem !== 'function'
  ) {
    return baseState;
  }

  try {
    const raw = localStorage.getItem(MEMBER_STORAGE_KEY);
    if (!raw) return baseState;
    const parsed = JSON.parse(raw);
    return reducer(baseState, { type: 'hydrate', payload: parsed });
  } catch {
    return baseState;
  }
}

export function reducer(state, action) {
  switch (action.type) {
    case 'hydrate':
      return {
        ...state,
        ...serializeMemberState(action.payload),
        notice: null,
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
        integrations: upsertBy(state.integrations, action.payload, 'platform'),
        notice: buildNotice('startIntegration', action.payload),
      };
    case 'removeIntegration':
      return {
        ...state,
        integrations: state.integrations.filter((entry) => entry?.platform !== action.payload),
      };
    case 'updatePreferences':
      return {
        ...state,
        preferences: normalizePreferences(action.payload, state.preferences),
        notice: buildNotice('preferences'),
      };
    case 'importLocalState':
      return {
        ...state,
        ...serializeMemberState(action.payload),
        notice: buildNotice('importLocalState'),
      };
    case 'clearLocalState': {
      const reset = createInitialMemberState();
      return {
        ...state,
        ...reset,
        notice: buildNotice('clearLocalState'),
      };
    }
    case 'clearNotice':
      return {
        ...state,
        notice: null,
      };
    default:
      return state;
  }
}
