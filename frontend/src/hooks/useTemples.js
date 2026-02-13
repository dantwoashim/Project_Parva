/**
 * useTemples Hook
 * ===============
 * 
 * Fetches temple data from the backend API.
 */

import { useState, useEffect } from 'react';
import { fetchAPI } from '../services/api';

/**
 * Hook to fetch all temples
 */
export function useTemples() {
    const [temples, setTemples] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTemples = async () => {
            try {
                setLoading(true);
                const data = await fetchAPI('/temples');
                setTemples(data.temples || []);
                setError(null);
            } catch (err) {
                setError(err.message);
                setTemples([]);
            } finally {
                setLoading(false);
            }
        };

        fetchTemples();
    }, []);

    return { temples, loading, error };
}

/**
 * Hook to fetch temples for a specific festival
 */
export function useTemplesForFestival(festivalId) {
    const [temples, setTemples] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!festivalId) {
            setTemples([]);
            return;
        }

        const fetchTemples = async () => {
            try {
                setLoading(true);
                const data = await fetchAPI(`/temples/for-festival/${festivalId}`);
                // Transform to include role in temple object
                const templesWithRoles = (data.temples || []).map(t => ({
                    ...t.temple,
                    role: t.role
                }));
                setTemples(templesWithRoles);
                setError(null);
            } catch (err) {
                setError(err.message);
                setTemples([]);
            } finally {
                setLoading(false);
            }
        };

        fetchTemples();
    }, [festivalId]);

    return { temples, loading, error };
}

/**
 * Hook to fetch a single temple's details
 */
export function useTempleDetail(templeId) {
    const [temple, setTemple] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!templeId) {
            setTemple(null);
            return;
        }

        const fetchTemple = async () => {
            try {
                setLoading(true);
                const data = await fetchAPI(`/temples/${templeId}`);
                setTemple(data);
                setError(null);
            } catch (err) {
                setError(err.message);
                setTemple(null);
            } finally {
                setLoading(false);
            }
        };

        fetchTemple();
    }, [templeId]);

    return { temple, loading, error };
}

export default useTemples;
