/**
 * useFestivals Hook
 * =================
 * 
 * Fetches and manages festival list state.
 */

import { useState, useEffect, useCallback } from 'react';
import { festivalAPI } from '../services/api';

/**
 * Hook to fetch and manage festivals list.
 * 
 * @param {Object} options
 * @param {string} options.category - Filter by category
 * @param {string} options.search - Search query
 * @returns {Object} Festival state and actions
 */
export function useFestivals({ category, search, qualityBand = "computed", algorithmicOnly = true } = {}) {
    const [festivals, setFestivals] = useState([]);
    const [total, setTotal] = useState(0);
    const [scoreboard, setScoreboard] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchFestivals = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const params = {
                quality_band: qualityBand,
                algorithmic_only: String(algorithmicOnly),
            };
            if (category) params.category = category;
            if (search) params.search = search;

            const [data, scoreboardPayload] = await Promise.all([
                festivalAPI.getAll(params),
                festivalAPI.getCoverageScoreboard(),
            ]);
            setFestivals(data.festivals || []);
            setTotal(data.total || 0);
            setScoreboard(scoreboardPayload || null);
        } catch (err) {
            setError(err.message || 'Failed to load festivals');
            setFestivals([]);
            setScoreboard(null);
        } finally {
            setLoading(false);
        }
    }, [category, search, qualityBand, algorithmicOnly]);

    useEffect(() => {
        fetchFestivals();
    }, [fetchFestivals]);

    return {
        festivals,
        total,
        scoreboard,
        loading,
        error,
        refetch: fetchFestivals,
    };
}

/**
 * Hook to fetch upcoming festivals.
 * 
 * @param {number} days - Days to look ahead
 * @returns {Object} Upcoming festivals state
 */
export function useUpcomingFestivals(days = 90, qualityBand = "computed") {
    const [festivals, setFestivals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchUpcoming = async () => {
            setLoading(true);
            setError(null);

            try {
                const data = await festivalAPI.getUpcoming(days, qualityBand);
                setFestivals(data.festivals || []);
            } catch (err) {
                setError(err.message || 'Failed to load upcoming festivals');
                setFestivals([]);
            } finally {
                setLoading(false);
            }
        };

        fetchUpcoming();
    }, [days, qualityBand]);

    return { festivals, loading, error };
}

/**
 * Hook to fetch single festival detail.
 * 
 * @param {string} festivalId - Festival ID
 * @param {number|null} year - Optional year for date calculation
 * @returns {Object} Festival detail state
 */
export function useFestivalDetail(festivalId, year = null) {
    const [festival, setFestival] = useState(null);
    const [dates, setDates] = useState(null);
    const [nearbyFestivals, setNearbyFestivals] = useState([]);
    const [meta, setMeta] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!festivalId) {
            setFestival(null);
            setDates(null);
            setNearbyFestivals([]);
            setMeta(null);
            return;
        }

        const fetchDetail = async () => {
            setLoading(true);
            setError(null);

            try {
                const envelope = await festivalAPI.getByIdEnvelope(festivalId, year || undefined);
                const data = envelope.data || {};
                setFestival(data.festival);
                setDates(data.dates || null);
                setNearbyFestivals(data.nearby_festivals || []);
                setMeta(envelope.meta || null);
            } catch (err) {
                setError(err.message || 'Failed to load festival details');
                setFestival(null);
                setDates(null);
                setNearbyFestivals([]);
                setMeta(null);
            } finally {
                setLoading(false);
            }
        };

        fetchDetail();
    }, [festivalId, year]);

    return { festival, dates, nearbyFestivals, meta, loading, error };
}

/**
 * Hook to fetch festival dates for multiple years.
 * 
 * @param {string} festivalId - Festival ID
 * @param {number} years - Number of years to fetch
 * @returns {Object} Dates state
 */
export function useFestivalDates(festivalId, years = 3) {
    const [dates, setDates] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!festivalId) {
            setDates([]);
            return;
        }

        const fetchDates = async () => {
            setLoading(true);
            setError(null);

            try {
                const data = await festivalAPI.getDates(festivalId, years);
                setDates(Array.isArray(data) ? data : (data.dates || []));
            } catch (err) {
                setError(err.message || 'Failed to load festival dates');
                setDates([]);
            } finally {
                setLoading(false);
            }
        };

        fetchDates();
    }, [festivalId, years]);

    return { dates, loading, error };
}

export default useFestivals;
