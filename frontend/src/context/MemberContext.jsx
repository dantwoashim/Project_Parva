import { useEffect, useMemo, useReducer } from 'react';
import PropTypes from 'prop-types';
import { MemberContext } from './memberContextShared';
import {
  MEMBER_STORAGE_KEY,
  loadInitialMemberState,
  reducer,
  serializeMemberState,
} from './memberContextState';
import { trackEvent } from '../services/analytics';

function queueMemberAction(dispatch, reason, pendingAction, successEvent) {
  trackEvent('save_attempted', {
    reason,
    kind: pendingAction.kind,
  });

  dispatch({ type: pendingAction.kind, payload: pendingAction.payload });
  if (successEvent) {
    trackEvent(successEvent, {
      reason,
      kind: pendingAction.kind,
    });
  }
  return true;
}

export function MemberProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, undefined, loadInitialMemberState);

  useEffect(() => {
    try {
      if (typeof localStorage?.setItem !== 'function') return;
      localStorage.setItem(MEMBER_STORAGE_KEY, JSON.stringify(serializeMemberState(state)));
    } catch {
      // Ignore local storage write issues.
    }
  }, [state]);

  const value = useMemo(() => ({
    state,
    savePlace: (place) => queueMemberAction(dispatch, 'save_place', { kind: 'savePlace', payload: place }, 'save_completed'),
    saveFestival: (festival) => queueMemberAction(dispatch, 'save_festival', { kind: 'saveFestival', payload: festival }, 'save_completed'),
    removeFestival: (festivalId) => dispatch({ type: 'removeFestival', payload: festivalId }),
    saveReading: (reading) => queueMemberAction(dispatch, 'save_reading', { kind: 'saveReading', payload: reading }, 'save_completed'),
    removeReading: (readingId) => dispatch({ type: 'removeReading', payload: readingId }),
    removePlace: (placeId) => dispatch({ type: 'removePlace', payload: placeId }),
    toggleReminder: (reminder) => queueMemberAction(dispatch, 'reminder', { kind: 'toggleReminder', payload: reminder }, 'reminder_created'),
    removeReminder: (reminderId) => dispatch({ type: 'removeReminder', payload: reminderId }),
    startIntegration: (integration) => queueMemberAction(dispatch, 'calendar_integration', { kind: 'startIntegration', payload: integration }, 'calendar_integration_started'),
    removeIntegration: (platform) => dispatch({ type: 'removeIntegration', payload: platform }),
    updatePreferences: (preferences) => dispatch({ type: 'updatePreferences', payload: preferences }),
    importLocalState: (payload) => dispatch({ type: 'importLocalState', payload }),
    clearLocalState: () => dispatch({ type: 'clearLocalState' }),
    clearNotice: () => dispatch({ type: 'clearNotice' }),
  }), [state]);

  return <MemberContext.Provider value={value}>{children}</MemberContext.Provider>;
}

MemberProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
