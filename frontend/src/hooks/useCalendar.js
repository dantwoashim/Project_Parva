/**
 * useCalendar Hook
 * ================
 *
 * Calendar conversion and tithi information hooks.
 */

import { useEffect, useState } from 'react';
import { calendarAPI } from '../services/api';

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
            formatted:
              data.bikram_sambat?.formatted ||
              `${data.bikram_sambat?.year} ${data.bikram_sambat?.month_name} ${data.bikram_sambat?.day}`,
            confidence: data.bikram_sambat?.confidence,
            sourceRange: data.bikram_sambat?.source_range || null,
            estimatedErrorDays: data.bikram_sambat?.estimated_error_days || null,
          },
          lunar: {
            phase: 0,
            phaseName: tithi.moon_phase,
            tithi: tithi.tithi,
            paksha: tithi.paksha,
            pakshaName:
              tithi.paksha === 'shukla'
                ? 'Shukla Paksha (Bright)'
                : 'Krishna Paksha (Dark)',
            illumination: 0.5,
            method: tithi.method,
            confidence: tithi.confidence,
            referenceTime: tithi.reference_time,
            sunriseUsed: tithi.sunrise_used,
          },
          lastUpdated: new Date(),
        });
      } catch (err) {
        setError(err.message || 'Failed to load calendar data');
        setCalendarInfo(null);
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
