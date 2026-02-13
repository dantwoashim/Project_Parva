/**
 * FestivalDetail Component
 * ========================
 * 
 * Full festival detail view with tabbed content.
 * Slides in from right as a drawer.
 */

import { useState } from 'react';
import PropTypes from 'prop-types';
import { format } from 'date-fns';
import { MythologySection } from './MythologySection';
import { RitualTimeline } from './RitualTimeline';
import { ConnectionsView } from './ConnectionsView';
import { ExplainPanel } from './ExplainPanel';
import { festivalAPI } from '../../services/api';
import './FestivalDetail.css';

const TABS = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'mythology', label: 'Mythology', icon: '📜' },
    { id: 'ritual', label: 'Rituals', icon: '🪔' },
    { id: 'connections', label: 'Connections', icon: '🔗' },
];

/**
 * Normalize ritual data to RitualTimeline expected format.
 * RitualTimeline expects { days: [...], preparation: string }
 */
function normalizeRitualData(festival) {
    // If already normalized shape
    if (festival.daily_rituals?.days && Array.isArray(festival.daily_rituals.days)) {
        return festival.daily_rituals;
    }

    // Backend shape: daily_rituals is an array of day objects with `rituals`
    if (Array.isArray(festival.daily_rituals) && festival.daily_rituals.length > 0) {
        return {
            days: festival.daily_rituals.map((day, index) => ({
                name: day.name || `Day ${day.day || index + 1}`,
                significance: day.description || null,
                events: (day.rituals || []).map(step => ({
                    time: step.time_of_day || null,
                    title: step.name || 'Ritual',
                    description: step.description || null,
                    location: step.location || null,
                    offerings: step.items_needed || null,
                })),
            })),
        };
    }

    // If simple_rituals is an array, wrap in days structure
    if (Array.isArray(festival.simple_rituals)) {
        return {
            days: [{
                name: festival.name,
                events: festival.simple_rituals.map(step => ({
                    time: step.time_of_day || null,
                    title: step.name || 'Ritual',
                    description: step.description || null,
                    location: step.location || null,
                    offerings: step.items_needed || null,
                }))
            }]
        };
    }

    // If simple_rituals has days property
    if (festival.simple_rituals?.days) {
        return festival.simple_rituals;
    }

    // Return null to show empty state
    return null;
}

/**
 * FestivalDetail displays complete festival information with tabs.
 * 
 * @param {Object} props
 * @param {Object} props.festival - Full festival object
 * @param {Object} props.dates - Festival dates
 * @param {Function} props.onClose - Close handler
 * @param {Function} props.onLocationClick - Handler for location clicks
 * @param {Array} props.allFestivals - All festivals for connection links
 * @param {Function} props.onFestivalClick - Handler for clicking related festivals
 */
export function FestivalDetail({
    festival,
    dates,
    onClose,
    onLocationClick,
    allFestivals = [],
    onFestivalClick,
}) {
    const [activeTab, setActiveTab] = useState('overview');
    const [showExplain, setShowExplain] = useState(false);
    const [explainData, setExplainData] = useState(null);
    const [explainLoading, setExplainLoading] = useState(false);
    const [explainError, setExplainError] = useState(null);

    if (!festival) return null;

    const formatDateRange = () => {
        if (!dates?.start_date) return 'Date TBD';
        const start = new Date(dates.start_date);
        const end = dates.end_date ? new Date(dates.end_date) : start;

        if (start.getTime() === end.getTime()) {
            return format(start, 'MMMM d, yyyy');
        }
        return `${format(start, 'MMMM d')} - ${format(end, 'd, yyyy')}`;
    };

    const handleOpenExplain = async () => {
        setShowExplain(true);
        setExplainLoading(true);
        setExplainError(null);
        try {
            const year = dates?.start_date ? new Date(dates.start_date).getFullYear() : new Date().getFullYear();
            const data = await festivalAPI.getExplain(festival.id, year);
            setExplainData(data);
        } catch (err) {
            setExplainError(err.message || 'Failed to load explanation');
            setExplainData(null);
        } finally {
            setExplainLoading(false);
        }
    };

    return (
        <div className="festival-detail animate-slide-in-right">
            {/* Header */}
            <header className="festival-detail__header">
                <button
                    className="festival-detail__close btn btn-secondary"
                    onClick={onClose}
                    aria-label="Close festival detail"
                >
                    ← Back
                </button>

                {/* Hero */}
                <div
                    className="festival-detail__hero"
                    style={{ backgroundColor: festival.primary_color || 'var(--color-primary)' }}
                >
                    <div className="hero-gradient" />

                    {/* Badges */}
                    <div className="hero-badges">
                        <span className="badge">{festival.category}</span>
                        {festival.significance_level && (
                            <span className="badge badge-gold">
                                {'★'.repeat(festival.significance_level)}
                            </span>
                        )}
                    </div>
                </div>

                {/* Titles */}
                <div className="festival-detail__titles">
                    <h1 className="text-display">{festival.name}</h1>
                    {festival.name_nepali && (
                        <span className="title-nepali text-nepali">{festival.name_nepali}</span>
                    )}
                    <p className="title-date">{formatDateRange()}</p>
                    {festival.tagline && (
                        <p className="title-tagline">{festival.tagline}</p>
                    )}
                    <button className="btn btn-secondary" onClick={handleOpenExplain}>
                        Why this date?
                    </button>
                </div>

                {/* Tabs */}
                <nav className="festival-detail__tabs" role="tablist">
                    {TABS.map(tab => (
                        <button
                            key={tab.id}
                            role="tab"
                            aria-selected={activeTab === tab.id}
                            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab.id)}
                        >
                            <span className="tab-icon">{tab.icon}</span>
                            <span className="tab-label">{tab.label}</span>
                        </button>
                    ))}
                </nav>
            </header>

            {/* Content */}
            <div className="festival-detail__content">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                    <div className="tab-panel animate-fade-in" role="tabpanel">
                        <section className="content-section">
                            <h2>About {festival.name}</h2>
                            <p className="summary-text">
                                {festival.description || 'Festival description coming soon...'}
                            </p>
                        </section>

                        {/* Quick Facts */}
                        <section className="content-section">
                            <h3>Quick Facts</h3>
                            <ul className="quick-facts">
                                <li>
                                    <span className="fact-icon">📅</span>
                                    <span className="fact-label">Duration</span>
                                    <span className="fact-value">{festival.duration_days || 1} days</span>
                                </li>
                                <li>
                                    <span className="fact-icon">🗓️</span>
                                    <span className="fact-label">Calendar</span>
                                    <span className="fact-value">{festival.calendar_type || 'lunar'}</span>
                                </li>
                                {festival.regional_focus?.length > 0 && (
                                    <li>
                                        <span className="fact-icon">📍</span>
                                        <span className="fact-label">Region</span>
                                        <span className="fact-value">{festival.regional_focus.join(', ')}</span>
                                    </li>
                                )}
                            </ul>
                        </section>

                        {/* Related Festivals Preview */}
                        {festival.related_festivals?.length > 0 && (
                            <section className="content-section">
                                <h3>Related Festivals</h3>
                                <div className="related-tags">
                                    {festival.related_festivals.map(id => (
                                        <span key={id} className="badge">{id}</span>
                                    ))}
                                </div>
                            </section>
                        )}
                    </div>
                )}

                {/* Mythology Tab */}
                {activeTab === 'mythology' && (
                    <div className="tab-panel animate-fade-in" role="tabpanel">
                        <MythologySection mythology={festival.mythology} />
                    </div>
                )}

                {/* Ritual Tab */}
                {activeTab === 'ritual' && (
                    <div className="tab-panel animate-fade-in" role="tabpanel">
                        <RitualTimeline
                            ritualSequence={normalizeRitualData(festival)}
                            onLocationClick={onLocationClick}
                        />
                    </div>
                )}

                {/* Connections Tab */}
                {activeTab === 'connections' && (
                    <div className="tab-panel animate-fade-in" role="tabpanel">
                        <ConnectionsView
                            festival={festival}
                            allFestivals={allFestivals}
                            onFestivalClick={onFestivalClick}
                            onDeityClick={(deity) => console.log('Deity clicked:', deity)}
                        />
                    </div>
                )}
            </div>

            {showExplain && (
                <ExplainPanel
                    data={explainData}
                    loading={explainLoading}
                    error={explainError}
                    onClose={() => setShowExplain(false)}
                />
            )}
        </div>
    );
}

FestivalDetail.propTypes = {
    festival: PropTypes.shape({
        id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        name_nepali: PropTypes.string,
        tagline: PropTypes.string,
        description: PropTypes.string,
        category: PropTypes.string,
        calendar_type: PropTypes.string,
        duration_days: PropTypes.number,
        regional_focus: PropTypes.arrayOf(PropTypes.string),
        primary_color: PropTypes.string,
        significance_level: PropTypes.number,
        mythology: PropTypes.object,
        daily_rituals: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
        simple_rituals: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
        related_festivals: PropTypes.arrayOf(PropTypes.string),
        connected_deities: PropTypes.arrayOf(PropTypes.string),
    }),
    dates: PropTypes.shape({
        start_date: PropTypes.string,
        end_date: PropTypes.string,
    }),
    onClose: PropTypes.func.isRequired,
    onLocationClick: PropTypes.func,
    allFestivals: PropTypes.array,
    onFestivalClick: PropTypes.func,
};

export default FestivalDetail;
