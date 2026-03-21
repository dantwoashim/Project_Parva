import { useEffect, useState } from 'react';
import { festivalAPI, muhurtaAPI, temporalAPI } from '../services/api';
import { describeSupportError, pickRejectedReason } from '../services/errorFormatting';

export function useTodayBundle({
  date,
  latitude,
  longitude,
  timezone,
  upcomingDays = 30,
  muhurtaType = 'general',
  fallbackErrorMessage = 'Today guidance is temporarily unavailable.',
}) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [compass, setCompass] = useState(null);
  const [compassMeta, setCompassMeta] = useState(null);
  const [muhurta, setMuhurta] = useState(null);
  const [muhurtaMeta, setMuhurtaMeta] = useState(null);
  const [onDateFestivals, setOnDateFestivals] = useState([]);
  const [upcomingFestivals, setUpcomingFestivals] = useState([]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      const [compassResult, muhurtaResult, onDateResult, upcomingResult] = await Promise.allSettled([
        temporalAPI.getCompassEnvelope({
          date,
          lat: latitude,
          lon: longitude,
          tz: timezone,
          qualityBand: 'computed',
        }),
        muhurtaAPI.getHeatmapEnvelope({
          date,
          lat: latitude,
          lon: longitude,
          tz: timezone,
          type: muhurtaType,
        }),
        festivalAPI.getOnDate(date),
        festivalAPI.getUpcoming(upcomingDays, 'computed'),
      ]);

      if (cancelled) return;

      if (compassResult.status === 'fulfilled') {
        setCompass(compassResult.value.data || null);
        setCompassMeta(compassResult.value.meta || null);
      } else {
        setCompass(null);
        setCompassMeta(null);
      }

      if (muhurtaResult.status === 'fulfilled') {
        setMuhurta(muhurtaResult.value.data || null);
        setMuhurtaMeta(muhurtaResult.value.meta || null);
      } else {
        setMuhurta(null);
        setMuhurtaMeta(null);
      }

      setOnDateFestivals(
        onDateResult.status === 'fulfilled' && Array.isArray(onDateResult.value)
          ? onDateResult.value
          : [],
      );
      setUpcomingFestivals(
        upcomingResult.status === 'fulfilled' && Array.isArray(upcomingResult.value?.festivals)
          ? upcomingResult.value.festivals
          : [],
      );

      setError(
        compassResult.status === 'rejected' && muhurtaResult.status === 'rejected'
          ? describeSupportError(
              pickRejectedReason(compassResult, muhurtaResult),
              fallbackErrorMessage,
            )
          : null,
      );
      setLoading(false);
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [date, fallbackErrorMessage, latitude, longitude, muhurtaType, timezone, upcomingDays]);

  return {
    loading,
    error,
    compass,
    compassMeta,
    muhurta,
    muhurtaMeta,
    onDateFestivals,
    upcomingFestivals,
  };
}

export default useTodayBundle;
