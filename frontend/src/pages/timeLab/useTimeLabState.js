import { useDeferredValue, useEffect, useMemo, useState, useTransition } from 'react';
import { todayIso } from '../../context/temporalContextState';
import { calendarAPI } from '../../services/api';
import {
  buildDefaultQuery,
  buildPresetCatalog,
  buildTimeLabResult,
  dayLimitForQuery,
  engineLabel,
  formatInputSignature,
  modeSummary,
  parseQuery,
  resolveAnchoredConversion,
} from './timeLabHelpers';
import { buildHorizonDescriptor } from '../../lib/chronologyProjection';

export function useTimeLabState(timezone) {
  const todayQuery = useMemo(() => buildDefaultQuery(todayIso(timezone)), [timezone]);
  const initialQuery = todayQuery;
  const [draft, setDraft] = useState(initialQuery);
  const [activeQuery, setActiveQuery] = useState(initialQuery);
  const [isPresetPending, startPresetTransition] = useTransition();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const deferredDraft = useDeferredValue(draft);

  const presets = useMemo(() => buildPresetCatalog(initialQuery), [initialQuery]);
  const draftHorizon = useMemo(() => buildHorizonDescriptor(deferredDraft), [deferredDraft]);
  const dayLimit = useMemo(() => dayLimitForQuery(draft), [draft]);
  const signature = useMemo(() => formatInputSignature(deferredDraft), [deferredDraft]);

  useEffect(() => {
    let cancelled = false;

    async function run() {
      setLoading(true);
      setError(null);
      try {
        const normalized = parseQuery(activeQuery);
        const anchored = await resolveAnchoredConversion(normalized, calendarAPI);
        if (cancelled) return;
        setResult(buildTimeLabResult(normalized, anchored));
      } catch (nextError) {
        if (!cancelled) {
          setResult(null);
          setError(nextError?.message || 'The conversion engine could not stabilize this request.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void run();
    return () => {
      cancelled = true;
    };
  }, [activeQuery]);

  function patchDraft(patch) {
    setDraft((current) => {
      const next = { ...current, ...patch };
      const nextLimit = dayLimitForQuery(next);
      if (next.day > nextLimit) {
        next.day = nextLimit;
      }
      return next;
    });
  }

  function submitCurrentDraft(event) {
    event?.preventDefault?.();
    try {
      const normalized = parseQuery(draft);
      setActiveQuery(normalized);
    } catch (nextError) {
      setError(nextError?.message || 'The conversion engine could not stabilize this request.');
    }
  }

  function applyPreset(query) {
    startPresetTransition(() => {
      setDraft(query);
      setActiveQuery(query);
    });
  }

  function resetToToday() {
    setError(null);
    applyPreset(todayQuery);
  }

  const primaryResult = result?.anchored?.output || result?.experimental?.output || null;
  const primaryEngine = result?.anchored ? engineLabel(result.anchored.confidence) : 'Experimental horizon engine';
  const comparisonLabel = result?.anchored
    ? result.anchored.comparison?.match === true
      ? 'Official and estimated live paths agree on this date.'
      : result.anchored.comparison?.official && result.anchored.comparison?.estimated
        ? 'The live engine sees both an official and estimated track here.'
        : 'The live engine returned one stable answer for this query.'
    : 'No live engine path exists for this query, so the horizon model carries the entire result.';

  return {
    todayQuery,
    draft,
    result,
    loading,
    error,
    draftHorizon,
    dayLimit,
    signature,
    presets,
    isPresetPending,
    patchDraft,
    submitCurrentDraft,
    applyPreset,
    resetToToday,
    primaryResult,
    primaryEngine,
    comparisonLabel,
    modeSummary: result ? modeSummary(result) : primaryEngine,
  };
}
