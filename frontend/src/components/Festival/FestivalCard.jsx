/**
 * FestivalCard — Nepal × Ink Wash Edition
 */

import { useState } from 'react';
import PropTypes from 'prop-types';
import { differenceInDays, format } from 'date-fns';
import './FestivalCard.css';

const CATEGORY_COLORS = {
    national: 'var(--vermillion)',
    newari: 'var(--gold-soft)',
    hindu: 'var(--saffron)',
    buddhist: 'var(--jade)',
    regional: 'var(--indigo)',
};

export function FestivalCard({ festival, onClick, isActive = false }) {
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
        if (!endDate || startDate.getTime() === endDate.getTime()) return start;
        return `${start}–${format(endDate, 'd')}`;
    };

    const accentColor = CATEGORY_COLORS[festival.category] || 'var(--gold)';
    const countdownText = getCountdownText();

    return (
        <article
            className={`festival-card ink-card ${isActive ? 'festival-card--active' : ''}`}
            onClick={() => onClick?.(festival)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && onClick?.(festival)}
            style={{ '--card-accent': accentColor }}
        >
            {/* Accent stripe */}
            <div className="festival-card__accent" />

            <div className="festival-card__content">
                {/* Category + Countdown */}
                <div className="festival-card__top">
                    <span className={`badge badge-${festival.category || 'national'}`}>
                        {festival.category}
                    </span>
                    {countdownText && (
                        <span className="countdown-badge">{countdownText}</span>
                    )}
                </div>

                {/* Name */}
                <h3 className="festival-card__title">{festival.name}</h3>
                {festival.name_nepali && (
                    <span className="festival-card__nepali text-nepali">{festival.name_nepali}</span>
                )}

                {/* Date */}
                <div className="festival-card__date">
                    <span>{formatDateRange()}</span>
                    {festival.duration_days > 1 && (
                        <span className="festival-card__duration"> · {festival.duration_days} days</span>
                    )}
                </div>

                {/* Tagline */}
                {festival.tagline && (
                    <p className="festival-card__tagline">{festival.tagline}</p>
                )}
            </div>
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
