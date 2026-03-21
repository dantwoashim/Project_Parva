import { useEffect, useMemo, useRef, useState } from 'react';
import { buildConsumerFestivalsViewModel } from '../consumer/consumerViewModels';
import { festivalAPI } from '../services/api';
import { describeSupportError } from '../services/errorFormatting';
import { addIsoDays } from '../utils/isoDate';

function addDays(base, days) {
  return addIsoDays(base, days);
}

export function useFestivalExplorerData({
  date,
  timezone,
  savedFestivals = [],
  search = '',
  category = '',
  region = '',
  sort = 'chronological',
  fallbackErrorMessage = 'Festival timeline is unavailable right now.',
}) {
  const [payload, setPayload] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const hasPayloadRef = useRef(false);

  const fromDate = date;
  const toDate = useMemo(() => addDays(date, 180), [date]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const bootstrapping = !hasPayloadRef.current;
      setLoading(bootstrapping);
      setRefreshing(!bootstrapping);
      setError(null);

      try {
        const [todayFestivals, timelineEnvelope] = await Promise.all([
          festivalAPI.getOnDate(fromDate),
          festivalAPI.getTimelineEnvelope({
            from: fromDate,
            to: toDate,
            qualityBand: 'computed',
            category: category || undefined,
            region: region || undefined,
            search: search.trim() || undefined,
            sort: sort || 'chronological',
            lang: 'en',
          }),
        ]);

        if (cancelled) return;

        setPayload({
          ...(timelineEnvelope.data || {}),
          active_today: Array.isArray(todayFestivals) ? todayFestivals : [],
        });
        hasPayloadRef.current = true;
      } catch (reason) {
        if (cancelled) return;

        setPayload(null);
        setError(describeSupportError(reason, fallbackErrorMessage));
      } finally {
        if (!cancelled) {
          setLoading(false);
          setRefreshing(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [category, fallbackErrorMessage, fromDate, region, search, sort, toDate]);

  const viewModel = useMemo(
    () => buildConsumerFestivalsViewModel({
      payload,
      search,
      category,
      savedFestivals,
      temporalState: {
        language: 'en',
        timezone,
      },
    }),
    [category, payload, savedFestivals, search, timezone],
  );

  return {
    loading,
    refreshing,
    error,
    payload,
    viewModel,
  };
}

export default useFestivalExplorerData;
