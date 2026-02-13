/**
 * ConnectionsView Component
 * =========================
 * 
 * Shows related festivals and connected deities.
 * Part of FestivalDetail's Connections tab.
 */

import PropTypes from 'prop-types';
import { DeityCard } from './DeityCard';
import './ConnectionsView.css';

/**
 * ConnectionsView displays a festival's connections to deities and other festivals.
 */
export function ConnectionsView({
    festival,
    allFestivals = [],
    onFestivalClick,
    onDeityClick,
}) {
    if (!festival) return null;

    const connectedDeities = festival.connected_deities || [];
    const relatedFestivalIds = festival.related_festivals || [];

    // Find related festival objects
    const relatedFestivals = relatedFestivalIds
        .map(id => allFestivals.find(f => f.id === id))
        .filter(Boolean);

    const hasConnections = connectedDeities.length > 0 || relatedFestivals.length > 0;

    return (
        <div className="connections-view">
            {/* Intro */}
            <section className="connections-intro">
                <p>
                    Explore how <strong>{festival.name}</strong> connects to Nepal's
                    rich tapestry of deities, temples, and sacred celebrations.
                </p>
            </section>

            {/* Deities */}
            {connectedDeities.length > 0 && (
                <section className="connections-section">
                    <h3 className="section-title">
                        <span className="section-icon">🙏</span>
                        Associated Deities
                    </h3>
                    <div className="deity-grid">
                        {connectedDeities.map(deity => (
                            <DeityCard
                                key={deity}
                                deityName={deity}
                                onClick={onDeityClick}
                                size="medium"
                            />
                        ))}
                    </div>
                </section>
            )}

            {/* Related Festivals */}
            {relatedFestivals.length > 0 && (
                <section className="connections-section">
                    <h3 className="section-title">
                        <span className="section-icon">🎭</span>
                        Related Festivals
                    </h3>
                    <div className="related-festivals">
                        {relatedFestivals.map(related => (
                            <button
                                key={related.id}
                                className="related-festival-card"
                                onClick={() => onFestivalClick?.(related)}
                                style={{ '--festival-color': related.primary_color || '#ff6b35' }}
                            >
                                <div className="related-festival__badge">
                                    <span className="badge">{related.category}</span>
                                </div>
                                <h4 className="related-festival__name">{related.name}</h4>
                                {related.name_nepali && (
                                    <span className="related-festival__nepali text-nepali">
                                        {related.name_nepali}
                                    </span>
                                )}
                                {related.tagline && (
                                    <p className="related-festival__tagline">{related.tagline}</p>
                                )}
                                <span className="related-festival__arrow">→</span>
                            </button>
                        ))}
                    </div>
                </section>
            )}

            {/* Connection Hints */}
            {hasConnections && (
                <section className="connections-section connections-hints">
                    <h3 className="section-title">
                        <span className="section-icon">💡</span>
                        Connection Insights
                    </h3>
                    <ul className="hints-list">
                        {connectedDeities.includes('Shiva') && (
                            <li>Celebrated at <strong>Pashupatinath</strong> – Nepal's holiest Shiva temple.</li>
                        )}
                        {connectedDeities.includes('Vishnu') && (
                            <li>Visit <strong>Budhanilkantha</strong> for the reclining Vishnu statue.</li>
                        )}
                        {connectedDeities.includes('Kumari') && (
                            <li>The <strong>Living Goddess</strong> appears during the procession.</li>
                        )}
                        {relatedFestivals.some(f => f.category === 'newari') && (
                            <li>Part of the vibrant <strong>Newari</strong> cultural tradition.</li>
                        )}
                        {festival.duration_days > 5 && (
                            <li>One of Nepal's longest celebrations at <strong>{festival.duration_days} days</strong>.</li>
                        )}
                    </ul>
                </section>
            )}

            {/* Empty State */}
            {!hasConnections && (
                <div className="connections-empty">
                    <span className="empty-icon">🔗</span>
                    <h4>Connections Coming Soon</h4>
                    <p>
                        We're mapping the connections between {festival.name} and
                        Nepal's network of sacred traditions.
                    </p>
                </div>
            )}
        </div>
    );
}

ConnectionsView.propTypes = {
    festival: PropTypes.shape({
        id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        name_nepali: PropTypes.string,
        connected_deities: PropTypes.arrayOf(PropTypes.string),
        related_festivals: PropTypes.arrayOf(PropTypes.string),
        duration_days: PropTypes.number,
    }),
    allFestivals: PropTypes.array,
    onFestivalClick: PropTypes.func,
    onDeityClick: PropTypes.func,
};

export default ConnectionsView;
