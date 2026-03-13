import { useContext } from 'react';
import { TemporalContext } from './temporalContextShared';

export function useTemporalContext() {
  const value = useContext(TemporalContext);
  if (!value) {
    throw new Error('useTemporalContext must be used within a TemporalProvider');
  }
  return value;
}
