import { useEffect, useState } from 'react';
import { festivalAPI, personalAPI } from '../services/api';
import { describeSupportError } from '../services/errorFormatting';

export function usePersonalPlaceBundle({
  date,
  latitude,
  longitude,
  timezone,
  fallbackErrorMessage = 'Failed to load personal place guidance.',
}) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(null);
  const [contextPayload, setContextPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [contextMeta, setContextMeta] = useState(null);
  const [festivals, setFestivals] = useState([]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      const [panchangaResult, festivalsResult, contextResult] = await Promise.allSettled([
        personalAPI.getPanchangaEnvelope({
          date,
          lat: latitude,
          lon: longitude,
          tz: timezone,
        }),
        festivalAPI.getOnDate(date),
        personalAPI.getContextEnvelope({
          date,
          lat: latitude,
          lon: longitude,
          tz: timezone,
        }),
      ]);

      if (cancelled) return;

      try {
        if (panchangaResult.status === 'rejected') {
          throw panchangaResult.reason;
        }

        setPayload(panchangaResult.value.data || null);
        setMeta(panchangaResult.value.meta || null);
        setFestivals(
          festivalsResult.status === 'fulfilled' && Array.isArray(festivalsResult.value)
            ? festivalsResult.value
            : [],
        );
        setContextPayload(
          contextResult.status === 'fulfilled'
            ? contextResult.value.data || null
            : null,
        );
        setContextMeta(
          contextResult.status === 'fulfilled'
            ? contextResult.value.meta || null
            : null,
        );
      } catch (reason) {
        setPayload(null);
        setContextPayload(null);
        setMeta(null);
        setContextMeta(null);
        setFestivals([]);
        setError(describeSupportError(reason, fallbackErrorMessage));
      } finally {
        setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [date, fallbackErrorMessage, latitude, longitude, timezone]);

  return {
    loading,
    error,
    payload,
    contextPayload,
    meta,
    contextMeta,
    festivals,
  };
}

export default usePersonalPlaceBundle;
