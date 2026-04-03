import { startTransition, useEffect, useMemo, useReducer, useRef } from 'react';
import PropTypes from 'prop-types';
import { MemberContext } from './memberContextShared';
import {
  buildAccountSyncFailureNotice,
  buildPersistenceFailureNotice,
  createInitialMemberState,
  reducer,
} from './memberContextState';
import { createLocalGuestMemberStore } from './memberStore';
import { trackEvent } from '../services/analytics';

function buildSuccessEventPayload(reason, action, state) {
  return {
    reason,
    kind: action.type,
    persistence_store: state?.persistence?.store || 'unknown',
    persistence_scope: state?.persistence?.scope || 'unknown',
    revision: state?.persistence?.revision ?? null,
  };
}

function commitHydratedState(dispatch, nextState) {
  startTransition(() => {
    dispatch({ type: 'hydrate', payload: nextState });
  });
}

function buildWriteFailureState(state) {
  return {
    ...state,
    persistence: {
      ...state?.persistence,
      syncStatus: 'write_failed',
    },
    notice: buildPersistenceFailureNotice(),
  };
}

function buildHydrationFailureState(state) {
  return {
    ...state,
    account: {
      ...state?.account,
      lastSyncedAt: null,
    },
    persistence: {
      ...state?.persistence,
      syncStatus: 'sync_failed',
    },
    notice: buildAccountSyncFailureNotice(),
  };
}

function queueMemberAction(trackState, writeChainRef, dispatch, memberStore, reason, pendingAction, successEvent) {
  trackEvent('save_attempted', {
    reason,
    kind: pendingAction.type,
  });

  const run = async () => {
    const currentState = trackState.current;
    const nextDraft = reducer(currentState, pendingAction);

    try {
      const persistedState = await memberStore.save(nextDraft, { reason, action: pendingAction });
      trackState.current = persistedState;
      commitHydratedState(dispatch, persistedState);

      if (successEvent) {
        trackEvent(successEvent, buildSuccessEventPayload(reason, pendingAction, persistedState));
      }

      return true;
    } catch {
      const failedState = buildWriteFailureState(currentState);
      trackState.current = failedState;
      commitHydratedState(dispatch, failedState);
      trackEvent('save_failed', {
        reason,
        kind: pendingAction.type,
      });
      return false;
    }
  };

  const nextWrite = writeChainRef.current.then(run, run);
  writeChainRef.current = nextWrite.catch(() => false);
  return nextWrite;
}

export function MemberProvider({ children, store }) {
  const memberStore = useMemo(() => store ?? createLocalGuestMemberStore(), [store]);
  const [state, dispatch] = useReducer(
    reducer,
    undefined,
    () => memberStore.load?.() ?? createInitialMemberState(),
  );
  const stateRef = useRef(state);
  const writeChainRef = useRef(Promise.resolve(true));

  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  useEffect(() => {
    let cancelled = false;

    async function hydrateStore() {
      if (typeof memberStore.hydrate !== 'function') {
        return;
      }

      try {
        const hydratedState = await memberStore.hydrate(stateRef.current);
        if (cancelled || !hydratedState) return;
        stateRef.current = hydratedState;
        commitHydratedState(dispatch, hydratedState);
      } catch {
        if (cancelled) return;
        const failedState = buildHydrationFailureState(stateRef.current);
        stateRef.current = failedState;
        commitHydratedState(dispatch, failedState);
      }
    }

    hydrateStore();
    return () => {
      cancelled = true;
    };
  }, [memberStore]);

  const value = useMemo(() => ({
    state,
    savePlace: (place) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'save_place',
      { type: 'savePlace', payload: place },
      'save_completed',
    ),
    saveFestival: (festival) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'save_festival',
      { type: 'saveFestival', payload: festival },
      'save_completed',
    ),
    removeFestival: (festivalId) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'remove_festival',
      { type: 'removeFestival', payload: festivalId },
    ),
    saveReading: (reading) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'save_reading',
      { type: 'saveReading', payload: reading },
      'save_completed',
    ),
    removeReading: (readingId) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'remove_reading',
      { type: 'removeReading', payload: readingId },
    ),
    removePlace: (placeId) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'remove_place',
      { type: 'removePlace', payload: placeId },
    ),
    toggleReminder: (reminder) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'reminder',
      { type: 'toggleReminder', payload: reminder },
      'reminder_created',
    ),
    removeReminder: (reminderId) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'remove_reminder',
      { type: 'removeReminder', payload: reminderId },
    ),
    startIntegration: (integration) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'calendar_integration',
      { type: 'startIntegration', payload: integration },
      'calendar_integration_started',
    ),
    removeIntegration: (platform) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'remove_integration',
      { type: 'removeIntegration', payload: platform },
    ),
    updatePreferences: (preferences) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'preferences',
      { type: 'updatePreferences', payload: preferences },
    ),
    importLocalState: (payload) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'import_device_cache',
      { type: 'importLocalState', payload },
    ),
    clearLocalState: () => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      'clear_device_cache',
      { type: 'clearLocalState' },
    ),
    setLocalSaveConsent: (enabled) => queueMemberAction(
      stateRef,
      writeChainRef,
      dispatch,
      memberStore,
      enabled ? 'enable_local_save' : 'disable_local_save',
      { type: 'setLocalSaveConsent', payload: { enabled: Boolean(enabled) } },
    ),
    clearNotice: () => {
      startTransition(() => {
        dispatch({ type: 'clearNotice' });
      });
    },
  }), [memberStore, state]);

  return <MemberContext.Provider value={value}>{children}</MemberContext.Provider>;
}

MemberProvider.propTypes = {
  children: PropTypes.node.isRequired,
  store: PropTypes.shape({
    load: PropTypes.func,
    hydrate: PropTypes.func,
    save: PropTypes.func,
  }),
};
