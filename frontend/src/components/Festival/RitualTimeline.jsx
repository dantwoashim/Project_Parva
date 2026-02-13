/**
 * RitualTimeline Component
 * ========================
 * 
 * Displays festival ritual sequence as a vertical timeline.
 */

import { useState } from 'react';
import PropTypes from 'prop-types';
import './RitualTimeline.css';

/**
 * RitualTimeline displays the day-by-day ritual events.
 * 
 * @param {Object} props
 * @param {Object} props.ritualSequence - Ritual sequence object
 * @param {Function} props.onLocationClick - Handler for location clicks
 */
export function RitualTimeline({ ritualSequence, onLocationClick }) {
    const [selectedDay, setSelectedDay] = useState(0);
    const [expandedEvent, setExpandedEvent] = useState(null);

    if (!ritualSequence?.days?.length) {
        return (
            <div className="ritual-timeline ritual-timeline--empty">
                <div className="empty-state">
                    <span className="empty-icon">🪔</span>
                    <h3>Ritual Sequence Coming Soon</h3>
                    <p>
                        The detailed ritual timeline for this festival is being documented
                        and will be available in a future update.
                    </p>
                </div>
            </div>
        );
    }

    const { days, preparation } = ritualSequence;
    const currentDay = days[selectedDay];

    return (
        <div className="ritual-timeline">
            {/* Preparation Section */}
            {preparation && (
                <section className="ritual-prep">
                    <h3 className="prep-title">
                        <span className="prep-icon">📝</span>
                        Preparation
                    </h3>
                    <p className="prep-content">{preparation}</p>
                </section>
            )}

            {/* Day Selector */}
            {days.length > 1 && (
                <nav className="day-selector" role="tablist">
                    {days.map((day, index) => (
                        <button
                            key={index}
                            role="tab"
                            aria-selected={selectedDay === index}
                            className={`day-btn ${selectedDay === index ? 'active' : ''}`}
                            onClick={() => setSelectedDay(index)}
                        >
                            <span className="day-number">Day {index + 1}</span>
                            {day.name && <span className="day-name">{day.name}</span>}
                        </button>
                    ))}
                </nav>
            )}

            {/* Day Header */}
            <header className="day-header">
                <h2 className="day-title">
                    {currentDay.name || `Day ${selectedDay + 1}`}
                </h2>
                {currentDay.significance && (
                    <p className="day-significance">{currentDay.significance}</p>
                )}
            </header>

            {/* Timeline Events */}
            <div className="timeline-track">
                {currentDay.events?.map((event, index) => (
                    <article
                        key={index}
                        className={`timeline-event ${expandedEvent === index ? 'expanded' : ''}`}
                        onClick={() => setExpandedEvent(expandedEvent === index ? null : index)}
                    >
                        {/* Time Marker */}
                        <div className="event-time">
                            {event.time || '—'}
                        </div>

                        {/* Timeline Node */}
                        <div className="event-node">
                            <div className="node-dot" />
                            {index < currentDay.events.length - 1 && (
                                <div className="node-line" />
                            )}
                        </div>

                        {/* Event Content */}
                        <div className="event-content glass-card">
                            <h4 className="event-title">{event.title}</h4>

                            {event.location && (
                                <button
                                    className="event-location"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onLocationClick?.(event.location);
                                    }}
                                >
                                    📍 {event.location}
                                </button>
                            )}

                            {expandedEvent === index && (
                                <div className="event-details animate-fade-in">
                                    {event.description && (
                                        <p className="event-description">{event.description}</p>
                                    )}

                                    {event.participants && (
                                        <div className="event-participants">
                                            <span className="label">Participants:</span>
                                            <span>{event.participants}</span>
                                        </div>
                                    )}

                                    {event.offerings && (
                                        <div className="event-offerings">
                                            <span className="label">Offerings:</span>
                                            <span>{event.offerings.join(', ')}</span>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Expand Hint */}
                            <span className="event-expand-hint">
                                {expandedEvent === index ? '▲ Less' : '▼ More'}
                            </span>
                        </div>
                    </article>
                ))}
            </div>

            {/* No Events */}
            {!currentDay.events?.length && (
                <div className="no-events">
                    <p>No detailed events documented for this day yet.</p>
                </div>
            )}
        </div>
    );
}

RitualTimeline.propTypes = {
    ritualSequence: PropTypes.shape({
        preparation: PropTypes.string,
        days: PropTypes.arrayOf(PropTypes.shape({
            name: PropTypes.string,
            significance: PropTypes.string,
            events: PropTypes.arrayOf(PropTypes.shape({
                time: PropTypes.string,
                title: PropTypes.string.isRequired,
                description: PropTypes.string,
                location: PropTypes.string,
                participants: PropTypes.string,
                offerings: PropTypes.arrayOf(PropTypes.string),
            })),
        })),
    }),
    onLocationClick: PropTypes.func,
};

export default RitualTimeline;
