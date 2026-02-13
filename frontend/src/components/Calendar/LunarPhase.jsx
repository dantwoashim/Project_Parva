/**
 * LunarPhase Component
 * ====================
 * 
 * Displays current moon phase and tithi information.
 */

import PropTypes from 'prop-types';
import { useCalendar } from '../../hooks/useCalendar';
import './LunarPhase.css';

/**
 * LunarPhase displays current moon phase with visual indicator.
 */
export function LunarPhase({ compact = false }) {
    const { calendarInfo, loading } = useCalendar();

    if (loading || !calendarInfo) {
        return (
            <div className={`lunar-phase ${compact ? 'lunar-phase--compact' : ''}`}>
                <div className="moon-visual skeleton" />
            </div>
        );
    }

    const { lunar, bikramSambat } = calendarInfo;

    // Moon emoji based on phase name for API/local consistency.
    const phaseEmojiMap = {
        'New Moon': '🌑',
        'Waxing Crescent': '🌒',
        'First Quarter': '🌓',
        'Waxing Gibbous': '🌔',
        'Full Moon': '🌕',
        'Waning Gibbous': '🌖',
        'Last Quarter': '🌗',
        'Waning Crescent': '🌘',
    };
    const moonEmoji = phaseEmojiMap[lunar.phaseName] || '🌙';

    if (compact) {
        return (
            <div className="lunar-phase lunar-phase--compact" title={lunar.phaseName}>
                <span className="moon-emoji">{moonEmoji}</span>
                <span className="tithi-compact">
                    {lunar.paksha === 'shukla' ? 'श' : lunar.paksha === 'krishna' ? 'क' : '?'}{lunar.tithi}
                </span>
            </div>
        );
    }

    return (
        <div className="lunar-phase glass-card">
            <div className="lunar-phase__visual">
                <span className="moon-emoji">{moonEmoji}</span>
                <div className="illumination-bar">
                    <div
                        className="illumination-fill"
                        style={{ width: `${lunar.illumination * 100}%` }}
                    />
                </div>
            </div>

            <div className="lunar-phase__info">
                <div className="phase-name">{lunar.phaseName}</div>
                <div className="tithi-info">
                    <span className="tithi-label">Tithi:</span>
                    <span className="tithi-value">{lunar.tithi}</span>
                    <span className="paksha-badge badge">
                        {lunar.paksha === 'shukla' ? 'शुक्ल' : lunar.paksha === 'krishna' ? 'कृष्ण' : 'अज्ञात'}
                    </span>
                    <span
                        className="approx-badge"
                        title={`Method: ${lunar.method || 'unknown'} • Confidence: ${lunar.confidence || 'unknown'}`}
                    >
                        {lunar.confidence === 'exact' ? '✓' : '~'}
                    </span>
                </div>
                <div className="bs-date">
                    {bikramSambat.formatted}
                    {bikramSambat.confidence && (
                        <span
                            className="approx-note"
                            title={
                                bikramSambat.confidence === 'official'
                                    ? `Lookup range: ${bikramSambat.sourceRange || 'unknown'}`
                                    : `Estimated mode (expected error window: ${bikramSambat.estimatedErrorDays || '0-1'} day)`
                            }
                        >
                            ({bikramSambat.confidence})
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}

LunarPhase.propTypes = {
    compact: PropTypes.bool,
};

export default LunarPhase;
