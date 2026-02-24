import PropTypes from 'prop-types';
import './KnowledgePanel.css';

export function KnowledgePanel({ title, intro, sections, className = '', defaultOpen = [] }) {
  return (
    <section className={`knowledge-panel ink-card ${className}`.trim()} aria-label={title}>
      <header className="knowledge-panel__header">
        <p className="knowledge-panel__eyebrow">Explainability</p>
        <h2>{title}</h2>
        {intro && <p className="knowledge-panel__intro">{intro}</p>}
      </header>

      <div className="knowledge-panel__sections">
        {sections.map((section, index) => {
          const isOpen = defaultOpen.includes(section.id) || (!defaultOpen.length && index === 0);
          return (
            <details
              key={section.id || section.title || index}
              className="knowledge-section"
              open={isOpen}
            >
              <summary>
                <span className="knowledge-section__title">{section.title}</span>
                {section.description && (
                  <span className="knowledge-section__description">{section.description}</span>
                )}
              </summary>

              <ul className="knowledge-terms">
                {(section.terms || []).map((term) => (
                  <li key={term.name} className="knowledge-term">
                    <h3>{term.name}</h3>
                    <p>{term.meaning}</p>
                    {term.whyItMatters && (
                      <p className="knowledge-term__why">
                        <strong>Why it matters:</strong> {term.whyItMatters}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            </details>
          );
        })}
      </div>
    </section>
  );
}

KnowledgePanel.propTypes = {
  title: PropTypes.string.isRequired,
  intro: PropTypes.string,
  className: PropTypes.string,
  defaultOpen: PropTypes.arrayOf(PropTypes.string),
  sections: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      title: PropTypes.string.isRequired,
      description: PropTypes.string,
      terms: PropTypes.arrayOf(
        PropTypes.shape({
          name: PropTypes.string.isRequired,
          meaning: PropTypes.string.isRequired,
          whyItMatters: PropTypes.string,
        }),
      ),
    }),
  ).isRequired,
};

export default KnowledgePanel;
