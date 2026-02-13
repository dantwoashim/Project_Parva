/**
 * useCalendar Hook
 * ================
 * 
 * Calendar conversion and tithi information hooks.
 */

import { useState, useEffect } from 'react';
import { calendarAPI } from '../services/api';

/**
 * Calculate approximate Bikram Sambat date.
 * 
 * ⚠️ WARNING: This is a simplified approximation!
 * - BS months have variable lengths (29-32 days)
 * - This can be off by up to ~15 days near month boundaries
 * - For precise festival dates, use the backend API
 * 
 * Only use this for casual header display. Festival-critical dates
 * should come from the /api/calendar endpoints.
 * 
 * @param {Date} date - Gregorian date
 * @returns {Object} BS date info (approximate)
 */
function calculateBSDate(date) {
    // BS year is ~56.7 years ahead of AD
    // BS New Year is around April 14
    const year = date.getFullYear();
    const month = date.getMonth();
    const day = date.getDate();

    // Approximate BS year
    let bsYear = year + 56;
    if (month < 3 || (month === 3 && day < 14)) {
        bsYear += 1;
    }

    // Approximate BS month (1-indexed)
    // Baishakh (1) starts mid-April
    const monthOffsets = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9];
    let bsMonth = monthOffsets[month];

    const bsMonthNames = [
        'Baishakh', 'Jestha', 'Ashadh', 'Shrawan',
        'Bhadra', 'Ashwin', 'Kartik', 'Mangsir',
        'Poush', 'Magh', 'Falgun', 'Chaitra'
    ];

    return {
        year: bsYear,
        month: bsMonth,
        monthName: bsMonthNames[bsMonth - 1],
        formatted: `${bsYear} ${bsMonthNames[bsMonth - 1]}`,
    };
}

/**
 * Hook to get current calendar information.
 * 
 * @returns {Object} Calendar info including BS date and moon phase
 */
export function useCalendar() {
    const [calendarInfo, setCalendarInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadToday = async () => {
            setLoading(true);
            setError(null);

            const today = new Date();

            try {
                const data = await calendarAPI.getToday();
                const apiDate = new Date(data.gregorian);
                const tithi = data.tithi || {};

                setCalendarInfo({
                    gregorian: {
                        date: apiDate,
                        formatted: apiDate.toLocaleDateString('en-US', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                        }),
                    },
                    bikramSambat: {
                        year: data.bikram_sambat?.year,
                        month: data.bikram_sambat?.month,
                        day: data.bikram_sambat?.day,
                        monthName: data.bikram_sambat?.month_name,
                        formatted: data.bikram_sambat?.formatted || `${data.bikram_sambat?.year} ${data.bikram_sambat?.month_name} ${data.bikram_sambat?.day}`,
                        confidence: data.bikram_sambat?.confidence,
                        sourceRange: data.bikram_sambat?.source_range || null,
                        estimatedErrorDays: data.bikram_sambat?.estimated_error_days || null,
                    },
                    lunar: {
                        phase: 0,
                        phaseName: tithi.moon_phase,
                        tithi: tithi.tithi,
                        paksha: tithi.paksha,
                        pakshaName: tithi.paksha === 'shukla' ? 'Shukla Paksha (Bright)' : 'Krishna Paksha (Dark)',
                        illumination: 0.5,
                        method: tithi.method,
                        confidence: tithi.confidence,
                        referenceTime: tithi.reference_time,
                        sunriseUsed: tithi.sunrise_used,
                    },
                    lastUpdated: new Date(),
                });
            } catch (err) {
                // Fallback to minimal local data if backend is unavailable.
                const bsDate = calculateBSDate(today);
                setError(err.message || 'Failed to load calendar data');
                setCalendarInfo({
                    gregorian: {
                        date: today,
                        formatted: today.toLocaleDateString('en-US', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                        }),
                    },
                    bikramSambat: {
                        ...bsDate,
                        confidence: 'estimated',
                        sourceRange: null,
                        estimatedErrorDays: '0-1',
                    },
                    lunar: {
                        phase: 0,
                        phaseName: 'Unavailable',
                        tithi: '--',
                        paksha: null,
                        pakshaName: 'Unknown',
                        illumination: 0,
                        method: 'unavailable',
                        confidence: 'estimated',
                        referenceTime: 'none',
                        sunriseUsed: null,
                    },
                    lastUpdated: new Date(),
                });
            } finally {
                setLoading(false);
            }
        };

        loadToday();
    }, []);

    return { calendarInfo, loading, error };
}

/**
 * Hook to get calendar month view with festivals.
 * 
 * @param {number} year - Gregorian year
 * @param {number} month - Month (1-12)
 * @returns {Object} Month calendar data
 */
export function useCalendarMonth(year, month) {
    const [monthData, setMonthData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchMonth = async () => {
            setLoading(true);
            setError(null);

            try {
                const data = await calendarAPI.getMonth(year, month);
                setMonthData(data);
            } catch (err) {
                setError(err.message || 'Failed to load calendar');
                setMonthData(null);
            } finally {
                setLoading(false);
            }
        };

        fetchMonth();
    }, [year, month]);

    return { monthData, loading, error };
}

export default useCalendar;
