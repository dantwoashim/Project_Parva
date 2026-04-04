/**
 * ParvaPage - Main Festival Discovery Page
 * =========================================
 * 
 * Layout: Sidebar (TemporalNavigator) + Main Content Area + Detail Drawer
 */

import { useState } from 'react';
import { TemporalNavigator, LunarPhase } from '../components/Calendar';
import { FestivalCard, FestivalDetail } from '../components/Festival';
import { FestivalMap } from '../components/Map';
import { useUpcomingFestivals, useFestivalDetail } from '../hooks/useFestivals';
import { useCalendar } from '../hooks/useCalendar';
import { useTemples } from '../hooks/useTemples';
import './ParvaPage.css';

/**
 * ParvaPage is the main page for festival discovery.
 * Features upcoming festival sidebar and full detail view.
 */
export function ParvaPage() {
    const [selectedFestivalId, setSelectedFestivalId] = useState(null);
    const [mapFocusQuery, setMapFocusQuery] = useState(null);
    const { festivals, loading, error } = useUpcomingFestivals(90);
    const {
        festival: selectedFestival,
        dates: selectedFestivalDates,
        loading: detailLoading
    } = useFestivalDetail(selectedFestivalId);
    const { calendarInfo } = useCalendar();
    const { temples, loading: templesLoading } = useTemples();

    const handleFestivalSelect = (festival) => {
        setSelectedFestivalId(festival.id);
    };

    const handleCloseDetail = () => {
        setSelectedFestivalId(null);
    };

    const handleLocationClick = (location) => {
        const focus = typeof location === 'string'
            ? location
            : location?.name || location?.id || null;

        setMapFocusQuery(focus);
        // Reveal map surface so ritual location actions are immediately visible.
        setSelectedFestivalId(null);
    };

    return (
        <div className="parva-page">
            {/* Sidebar - Temporal Navigator */}
            <TemporalNavigator
                festivals={festivals}
                selectedId={selectedFestivalId}
                onFestivalSelect={handleFestivalSelect}
                loading={loading}
                error={error}
            />

            {/* Main Content Area */}
            <main className="parva-page__main">
                {/* Header */}
                <header className="parva-page__header">
                    <div className="header-content">
                        <h1 className="text-display">
                            <span className="header-icon">🎭</span>
                            Project Parva
                        </h1>
                        <p className="header-tagline">
                            Discover Nepal's Sacred Festivals
                        </p>
                    </div>

                    {/* Calendar Info */}
                    <div className="header-calendar">
                        <LunarPhase />
                        <div className="date-display">
                            <span className="date-gregorian">
                                {new Date().toLocaleDateString('en-US', {
                                    weekday: 'long',
                                    month: 'long',
                                    day: 'numeric',
                                    year: 'numeric',
                                })}
                            </span>
                            {calendarInfo?.bikramSambat && (
                                <span className="date-bs">
                                    {calendarInfo.bikramSambat.formatted}
                                </span>
                            )}
                        </div>
                    </div>
                </header>

                {/* Welcome Message (shown when no festival selected) */}
                {!selectedFestivalId && !loading && (
                    <div className="parva-page__welcome animate-fade-in">
                        <div className="welcome-card glass-card">
                            <h2 className="text-display">Welcome to Project Parva</h2>
                            <p>
                                Explore Nepal's rich festival heritage. Select a festival from the sidebar
                                to discover its mythology, rituals, and sacred locations.
                            </p>

                            {/* Quick Stats */}
                            <div className="welcome-stats">
                                <div className="stat">
                                    <span className="stat-value">{festivals.length}</span>
                                    <span className="stat-label">Upcoming Festivals</span>
                                </div>
                                <div className="stat">
                                    <span className="stat-value">25+</span>
                                    <span className="stat-label">Total Festivals</span>
                                </div>
                                <div className="stat">
                                    <span className="stat-value">8</span>
                                    <span className="stat-label">Deities</span>
                                </div>
                            </div>

                            {/* Featured Festivals Preview */}
                            {festivals.length > 0 && (
                                <div className="welcome-featured">
                                    <h3>Coming Up Next</h3>
                                    <div className="featured-cards">
                                        {festivals.slice(0, 2).map(festival => (
                                            <FestivalCard
                                                key={festival.id}
                                                festival={{
                                                    ...festival,
                                                    next_start: festival.start_date,
                                                    next_end: festival.end_date,
                                                }}
                                                onClick={handleFestivalSelect}
                                            />
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Map Section */}
                        <div className="welcome-map glass-card">
                            <h3>Festival Locations</h3>
                            <FestivalMap
                                temples={temples}
                                selectedFestival={selectedFestival}
                                onFestivalSelect={handleFestivalSelect}
                                onLocationClick={handleLocationClick}
                                focusQuery={mapFocusQuery}
                                isLoading={templesLoading}
                            />
                        </div>
                    </div>
                )}

                {/* Loading State for Detail */}
                {selectedFestivalId && detailLoading && (
                    <div className="parva-page__loading animate-fade-in">
                        <div className="detail-skeleton glass-card">
                            <div className="skeleton" style={{ height: '180px', marginBottom: '1rem' }} />
                            <div className="skeleton" style={{ height: '32px', width: '60%', marginBottom: '0.5rem' }} />
                            <div className="skeleton" style={{ height: '20px', width: '40%', marginBottom: '1rem' }} />
                            <div className="skeleton" style={{ height: '48px', marginBottom: '1rem' }} />
                            <div className="skeleton" style={{ height: '200px' }} />
                        </div>
                    </div>
                )}

                {/* Festival Detail (shown when festival selected) */}
                {selectedFestivalId && !detailLoading && selectedFestival && (
                    <div className="parva-page__detail">
                        <div className="detail-wrapper glass-card">
                            <FestivalDetail
                                festival={selectedFestival}
                                dates={selectedFestivalDates}
                                onClose={handleCloseDetail}
                                onLocationClick={handleLocationClick}
                                allFestivals={festivals}
                                onFestivalClick={handleFestivalSelect}
                            />
                        </div>
                    </div>
                )}

                {/* Error State for Detail */}
                {selectedFestivalId && !detailLoading && !selectedFestival && (
                    <div className="parva-page__error animate-fade-in">
                        <div className="error-card glass-card">
                            <span className="error-icon">😕</span>
                            <h3>Festival Not Found</h3>
                            <p>We couldn't load the details for this festival.</p>
                            <button className="btn btn-secondary" onClick={handleCloseDetail}>
                                Go Back
                            </button>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default ParvaPage;
