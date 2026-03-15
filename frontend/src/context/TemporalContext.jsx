import { useCallback, useEffect, useMemo, useReducer } from 'react';
import PropTypes from 'prop-types';
import { TemporalContext } from './temporalContextShared';
import { STORAGE_KEY, loadInitialState, reducer } from './temporalContextState';

export function TemporalProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, undefined, loadInitialState);

  const setDate = useCallback((date) => dispatch({ type: 'setDate', payload: date }), []);
  const setLocation = useCallback((location) => dispatch({ type: 'setLocation', payload: location }), []);
  const setTimezone = useCallback((timezone) => dispatch({ type: 'setTimezone', payload: timezone }), []);
  const setLanguage = useCallback((language) => dispatch({ type: 'setLanguage', payload: language }), []);
  const setTheme = useCallback((theme) => dispatch({ type: 'setTheme', payload: theme }), []);
  const setLastViewed = useCallback((path) => dispatch({ type: 'setLastViewed', payload: path }), []);

  useEffect(() => {
    try {
      if (typeof localStorage?.setItem !== 'function') {
        return;
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // Ignore local storage write issues.
    }
  }, [state]);

  const value = useMemo(() => ({
    state,
    setDate,
    setLocation,
    setTimezone,
    setLanguage,
    setTheme,
    setLastViewed,
  }), [setDate, setLanguage, setLastViewed, setLocation, setTheme, setTimezone, state]);

  return <TemporalContext.Provider value={value}>{children}</TemporalContext.Provider>;
}

TemporalProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
