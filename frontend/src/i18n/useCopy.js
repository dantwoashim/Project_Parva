import { useContext, useMemo } from 'react';
import { TemporalContext } from '../context/temporalContextShared';
import { translate } from './messages';

export function useCopy() {
  const temporal = useContext(TemporalContext);
  const language = temporal?.state?.language === 'ne' ? 'ne' : 'en';

  const copy = useMemo(
    () => (key, values = {}) => translate(language, key, values),
    [language],
  );

  return {
    copy,
    language,
  };
}
