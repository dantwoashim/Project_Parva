import { createContext, useContext, useEffect, useMemo, useReducer } from 'react';
import PropTypes from 'prop-types';

const STORAGE_KEY = 'parva.temporal_context.v2';

function todayIso() {
  return new Date(Date.now()).toISOString().slice(0, 10);
}

const initialState = {
  date: todayIso(),
  location: { latitude: 27.7172, longitude: 85.324 },
  timezone: 'Asia/Kathmandu',
  mode: 'observance',
  language: 'en',
  qualityBand: 'computed',
};

function reducer(state, action) {
  switch (action.type) {
    case 'hydrate':
      return { ...state, ...(action.payload || {}) };
    case 'setDate':
      return { ...state, date: action.payload };
    case 'setLocation':
      return { ...state, location: { ...state.location, ...(action.payload || {}) } };
    case 'setTimezone':
      return { ...state, timezone: action.payload || 'Asia/Kathmandu' };
    case 'setMode':
      return { ...state, mode: action.payload === 'authority' ? 'authority' : 'observance' };
    case 'setLanguage':
      return { ...state, language: action.payload === 'ne' ? 'ne' : 'en' };
    case 'setQualityBand':
      return { ...state, qualityBand: action.payload || 'computed' };
    default:
      return state;
  }
}

const TemporalContext = createContext(null);

export function TemporalProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      dispatch({ type: 'hydrate', payload: parsed });
    } catch {
      // Ignore malformed local storage.
    }
  }, []);

  useEffect(() => {
    try {
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

export function useTemporalContext() {
  const value = useContext(TemporalContext);
  if (!value) {
    throw new Error('useTemporalContext must be used within a TemporalProvider');
  }
  return value;
}

export default TemporalContext;
