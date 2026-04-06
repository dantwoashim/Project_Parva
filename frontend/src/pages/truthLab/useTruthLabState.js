import { useEffect, useMemo, useState } from 'react';
import { festivalAPI, reliabilityAPI } from '../../services/api';
import { describeSupportError } from '../../services/errorFormatting';
import { trackEvent } from '../../services/analytics';
import { buildTruthLabStats, todayYear } from './truthLabHelpers';

export function useTruthLabState() {
  const [year, setYear] = useState(todayYear());
  const [atlas, setAtlas] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [capsule, setCapsule] = useState(null);
  const [benchmark, setBenchmark] = useState(null);
  const [sourceReviewQueue, setSourceReviewQueue] = useState(null);
  const [boundarySuite, setBoundarySuite] = useState(null);
  const [differential, setDifferential] = useState(null);
  const [loading, setLoading] = useState(true);
  const [capsuleLoading, setCapsuleLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    trackEvent('truth_lab_opened', { source: 'route' });
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadAtlas() {
      setLoading(true);
      setError(null);
      setCapsule(null);
      try {
        const payload = await festivalAPI.getDisputeAtlas(year, 18);
        if (cancelled) return;
        setAtlas(payload);
        const first = payload?.disputes?.[0]?.festival_id || null;
        setSelectedId(first);
      } catch (err) {
        if (cancelled) return;
        setError(describeSupportError(err, 'Failed to load the dispute atlas'));
        setAtlas(null);
        setSelectedId(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadAtlas();
    return () => {
      cancelled = true;
    };
  }, [year]);

  useEffect(() => {
    let cancelled = false;
    async function loadReliabilityArtifacts() {
      try {
        const [differentialPayload, benchmarkPayload, reviewPayload, boundaryPayload] = await Promise.all([
          reliabilityAPI.getDifferentialManifest(),
          reliabilityAPI.getBenchmarkManifest(),
          reliabilityAPI.getSourceReviewQueue(),
          reliabilityAPI.getBoundarySuite(),
        ]);
        if (cancelled) return;
        setDifferential(differentialPayload?.differential || null);
        setBenchmark(benchmarkPayload?.benchmark || null);
        setSourceReviewQueue(reviewPayload?.queue || null);
        setBoundarySuite(boundaryPayload?.boundary_suite || null);
      } catch {
        if (cancelled) return;
        setDifferential(null);
        setBenchmark(null);
        setSourceReviewQueue(null);
        setBoundarySuite(null);
      }
    }
    loadReliabilityArtifacts();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadCapsule() {
      if (!selectedId) {
        setCapsule(null);
        return;
      }
      setCapsuleLoading(true);
      try {
        const payload = await festivalAPI.getProofCapsule(selectedId, year);
        if (!cancelled) setCapsule(payload);
      } catch {
        if (!cancelled) setCapsule(null);
      } finally {
        if (!cancelled) setCapsuleLoading(false);
      }
    }
    loadCapsule();
    return () => {
      cancelled = true;
    };
  }, [selectedId, year]);

  const stats = useMemo(() => buildTruthLabStats(atlas, year), [atlas, year]);

  return {
    year,
    setYear,
    atlas,
    selectedId,
    setSelectedId,
    capsule,
    benchmark,
    sourceReviewQueue,
    boundarySuite,
    differential,
    loading,
    capsuleLoading,
    error,
    stats,
  };
}
