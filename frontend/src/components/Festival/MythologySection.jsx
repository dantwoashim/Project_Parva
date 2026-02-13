/**
 * MythologySection Component
 * ==========================
 * 
 * Displays festival mythology with rich formatting.
 */

import PropTypes from 'prop-types';
import './MythologySection.css';

/**
 * MythologySection renders the mythology content for a festival.
 * 
 * @param {Object} props
 * @param {Object} props.mythology - Festival mythology object
 */
export function MythologySection({ mythology }) {
    if (!mythology) {
        return (
            <div className="mythology-section mythology-section--empty">
                <div className="empty-state">
                    <span className="empty-icon">📜</span>
                    <h3>Mythology Coming Soon</h3>
                    <p>
                        The rich mythological history of this festival is being researched
                        and will be added in a future update.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="mythology-section">
            {/* Origin Story */}
            {mythology.origin_story && (
                <section className="mythology-story">
                    <h2 className="section-title">Origin Story</h2>
                    <div className="story-content">
                        {mythology.origin_story.split('\n\n').map((paragraph, i) => (
                            <p key={i}>{paragraph}</p>
                        ))}
                    </div>
                </section>
            )}

            {/* Scriptural References */}
            {mythology.scriptural_references?.length > 0 && (
                <section className="mythology-texts">
                    <h3 className="section-subtitle">Sacred Text References</h3>
                    <div className="text-badges">
                        {mythology.scriptural_references.map((text, i) => (
                            <span key={i} className="text-badge badge badge-gold">
                                📖 {text}
                            </span>
                        ))}
                    </div>
                </section>
            )}

            {/* Key Legends */}
            {mythology.legends?.length > 0 && (
                <section className="mythology-legends">
                    <h3 className="section-subtitle">Key Legends</h3>
                    <div className="legends-list">
                        {mythology.legends.map((legend, i) => (
                            <article key={i} className="legend-card glass-card">
                                <p className="legend-summary">{legend}</p>
                            </article>
                        ))}
                    </div>
                </section>
            )}

            {/* Cultural Significance / Summary */}
            {mythology.summary && (
                <section className="mythology-significance">
                    <h3 className="section-subtitle">About This Festival</h3>
                    <blockquote className="significance-quote">
                        {mythology.summary}
                    </blockquote>
                </section>
            )}

            {/* Historical Context */}
            {mythology.historical_context && (
                <section className="mythology-history">
                    <h3 className="section-subtitle">Historical Context</h3>
                    <p className="history-text">{mythology.historical_context}</p>
                </section>
            )}
        </div>
    );
}

MythologySection.propTypes = {
    mythology: PropTypes.shape({
        summary: PropTypes.string,
        origin_story: PropTypes.string,
        scriptural_references: PropTypes.arrayOf(PropTypes.string),
        legends: PropTypes.arrayOf(PropTypes.string),
        historical_context: PropTypes.string,
        regional_variations: PropTypes.object,
    }),
};

export default MythologySection;
