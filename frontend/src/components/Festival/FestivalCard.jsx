/**
 * FestivalCard Component
 * ======================
 * 
 * A visually stunning card displaying festival summary info.
 * Features glass effect, hover animations, and countdown badge.
 */

import { useState } from 'react';
import PropTypes from 'prop-types';
import { formatDistanceToNow, differenceInDays, format } from 'date-fns';
import './FestivalCard.css';

/**
 * FestivalCard displays a festival summary with image, dates, and countdown.
 * 
 * @param {Object} props
 * @param {Object} props.festival - Festival summary object
 * @param {Function} props.onClick - Handler when card is clicked
 * @param {boolean} props.isActive - Whether this card is currently selected
 */
export function FestivalCard({ festival, onClick, isActive = false }) {
    const [imageLoaded, setImageLoaded] = useState(false);

    // Calculate countdown
    const startDate = festival.next_start ? new Date(festival.next_start) : null;
    const daysUntil = startDate ? differenceInDays(startDate, new Date()) : null;

    const getCountdownText = () => {
        if (daysUntil === null) return null;
        if (daysUntil < 0) return 'Ongoing';
        if (daysUntil === 0) return 'Today!';
        if (daysUntil === 1) return 'Tomorrow';
        if (daysUntil < 7) return `${daysUntil} days`;
        if (daysUntil < 30) return `${Math.ceil(daysUntil / 7)} weeks`;
        return `${Math.ceil(daysUntil / 30)} months`;
    };

    const formatDateRange = () => {
        if (!startDate) return 'Date TBD';
        const endDate = festival.next_end ? new Date(festival.next_end) : null;

        const start = format(startDate, 'MMM d');
        if (!endDate || startDate.getTime() === endDate.getTime()) {
            return start;
        }
        const end = format(endDate, 'd');
        return `${start}-${end}`;
    };

    return (
        <article
            className={`festival-card glass-card ${isActive ? 'festival-card--active' : ''}`}
            onClick={() => onClick?.(festival)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && onClick?.(festival)}
        >
            {/* Hero Image Area */}
            <div className="festival-card__hero">
                <div
                    className={`festival-card__image ${imageLoaded ? 'loaded' : ''}`}
                    style={{
                        backgroundColor: festival.primary_color || 'var(--color-primary)',
                    }}
                >
                    {/* Gradient overlay */}
                    <div className="festival-card__gradient" />

                    {/* Category badge */}
                    <span className="festival-card__category badge">
                        {festival.category}
                    </span>

                    {/* Countdown badge */}
                    {daysUntil !== null && daysUntil >= 0 && (
                        <span className="festival-card__countdown countdown-badge">
                            <span className="countdown-icon">⏱</span>
                            {getCountdownText()}
                        </span>
                    )}
                </div>
            </div>

            {/* Content */}
            <div className="festival-card__content">
                {/* Festival names */}
                <div className="festival-card__names">
                    <h3 className="festival-card__title text-display">
                        {festival.name}
                    </h3>
                    {festival.name_nepali && (
                        <span className="festival-card__title-nepali text-nepali">
                            {festival.name_nepali}
                        </span>
                    )}
                </div>

                {/* Date range */}
                <div className="festival-card__date">
                    <span className="date-icon">📅</span>
                    <span>{formatDateRange()}</span>
                    {festival.duration_days > 1 && (
                        <span className="festival-card__duration">
                            ({festival.duration_days} days)
                        </span>
                    )}
                </div>

                {/* Tagline */}
                {festival.tagline && (
                    <p className="festival-card__tagline">
                        {festival.tagline}
                    </p>
                )}

                {/* Learn more button */}
                <button className="festival-card__cta btn btn-secondary">
                    Learn More
                    <span className="cta-arrow">→</span>
                </button>
            </div>

            {/* Active glow effect */}
            {isActive && <div className="festival-card__glow" />}
        </article>
    );
}

FestivalCard.propTypes = {
    festival: PropTypes.shape({
        id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        name_nepali: PropTypes.string,
        tagline: PropTypes.string,
        category: PropTypes.string,
        next_start: PropTypes.string,
        next_end: PropTypes.string,
        duration_days: PropTypes.number,
        primary_color: PropTypes.string,
    }).isRequired,
    onClick: PropTypes.func,
    isActive: PropTypes.bool,
};

export default FestivalCard;
