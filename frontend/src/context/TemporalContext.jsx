import { useEffect, useMemo, useReducer } from 'react';
import PropTypes from 'prop-types';
import { TemporalContext } from './temporalContextShared';
import { STORAGE_KEY, loadInitialState, reducer } from './temporalContextState';

export function TemporalProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, undefined, loadInitialState);

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
    setDate: (date) => dispatch({ type: 'setDate', payload: date }),
    setLocation: (location) => dispatch({ type: 'setLocation', payload: location }),
    setTimezone: (timezone) => dispatch({ type: 'setTimezone', payload: timezone }),
    setMode: (mode) => dispatch({ type: 'setMode', payload: mode }),
    setLanguage: (language) => dispatch({ type: 'setLanguage', payload: language }),
    setQualityBand: (qualityBand) => dispatch({ type: 'setQualityBand', payload: qualityBand }),
  }), [state]);

  return <TemporalContext.Provider value={value}>{children}</TemporalContext.Provider>;
}

TemporalProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
