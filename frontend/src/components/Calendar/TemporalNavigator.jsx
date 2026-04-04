/**
 * TemporalNavigator Component
 * ===========================
 * 
 * Sidebar showing upcoming festivals with date navigation.
 * Features: scrollable list, compact cards, countdown badges.
 */

import { useState } from 'react';
import PropTypes from 'prop-types';
import { FestivalCard } from '../Festival/FestivalCard';
import './TemporalNavigator.css';

/**
 * TemporalNavigator displays upcoming festivals in a sidebar.
 * 
 * @param {Object} props
 * @param {Array} props.festivals - List of upcoming festivals
 * @param {string} props.selectedId - Currently selected festival ID
 * @param {Function} props.onFestivalSelect - Handler for festival selection
 * @param {boolean} props.loading - Whether data is loading
 * @param {string} props.error - Error message if any
 */
export function TemporalNavigator({
    festivals = [],
    selectedId,
    onFestivalSelect,
    loading = false,
    error = null,
}) {
    const [timeRange, setTimeRange] = useState(30); // 30 or 90 days

    // Filter festivals based on time range
    const filteredFestivals = festivals.filter(f => {
        if (!f.days_until && f.days_until !== 0) return true;
        return f.days_until <= timeRange;
    });

    return (
        <aside className="temporal-navigator glass-card">
            {/* Header */}
            <header className="temporal-navigator__header">
                <h2 className="temporal-navigator__title text-display">
                    Upcoming Festivals
                </h2>

                {/* Time range toggle */}
                <div className="temporal-navigator__toggle">
                    <button
                        className={`toggle-btn ${timeRange === 30 ? 'active' : ''}`}
                        onClick={() => setTimeRange(30)}
                    >
                        30 Days
                    </button>
                    <button
                        className={`toggle-btn ${timeRange === 90 ? 'active' : ''}`}
                        onClick={() => setTimeRange(90)}
                    >
                        90 Days
                    </button>
                </div>
            </header>

            {/* Content */}
            <div className="temporal-navigator__content">
                {/* Loading State */}
                {loading && (
                    <div className="temporal-navigator__loading">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="festival-card-skeleton skeleton" />
                        ))}
                    </div>
                )}

                {/* Error State */}
                {error && !loading && (
                    <div className="temporal-navigator__error">
                        <span className="error-icon">⚠️</span>
                        <p>{error}</p>
                        <button className="btn btn-secondary" onClick={() => window.location.reload()}>
                            Retry
                        </button>
                    </div>
                )}

                {/* Empty State */}
                {!loading && !error && filteredFestivals.length === 0 && (
                    <div className="temporal-navigator__empty">
                        <span className="empty-icon">🎭</span>
                        <p>No festivals in the next {timeRange} days</p>
                        <button
                            className="btn btn-secondary"
                            onClick={() => setTimeRange(90)}
                        >
                            Show more
                        </button>
                    </div>
                )}

                {/* Festival List */}
                {!loading && !error && filteredFestivals.length > 0 && (
                    <ul className="temporal-navigator__list">
                        {filteredFestivals.map((festival, index) => (
                            <li
                                key={festival.id}
                                className="animate-slide-in-up"
                                style={{ animationDelay: `${index * 50}ms` }}
                            >
                                <FestivalCard
                                    festival={{
                                        ...festival,
                                        next_start: festival.start_date,
                                        next_end: festival.end_date,
                                    }}
                                    onClick={onFestivalSelect}
                                    isActive={festival.id === selectedId}
                                />
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {/* Footer with count */}
            <footer className="temporal-navigator__footer">
                <span className="festival-count">
                    {filteredFestivals.length} {filteredFestivals.length === 1 ? 'festival' : 'festivals'}
                </span>
            </footer>
        </aside>
    );
}

TemporalNavigator.propTypes = {
    festivals: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        start_date: PropTypes.string,
        days_until: PropTypes.number,
    })),
    selectedId: PropTypes.string,
    onFestivalSelect: PropTypes.func,
    loading: PropTypes.bool,
    error: PropTypes.string,
};

export default TemporalNavigator;
