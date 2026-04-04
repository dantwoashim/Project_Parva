import { useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { getInlineGlossaryEntry } from '../../data/inlineGlossary';
import './HoverGlossaryTerm.css';

export function HoverGlossaryTerm({
  term,
  label,
  className = '',
  inline = false,
  hideIcon = false,
  passive = false,
}) {
  const entry = getInlineGlossaryEntry(term);
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);

  if (!entry) {
    return <span className={className}>{label || term}</span>;
  }

  const triggerProps = passive
    ? {
        className: 'hover-glossary-term__trigger hover-glossary-term__trigger--passive',
      }
    : {
        type: 'button',
        className: 'hover-glossary-term__trigger',
        onFocus: () => setOpen(true),
        onBlur: (event) => {
          if (!rootRef.current?.contains(event.relatedTarget)) {
            setOpen(false);
          }
        },
        onKeyDown: (event) => {
          if (event.key === 'Escape') {
            setOpen(false);
            event.currentTarget.blur();
          }
        },
      };

  return (
    <span
      ref={rootRef}
      className={`hover-glossary-term ${inline ? 'hover-glossary-term--inline' : ''} ${open ? 'is-open' : ''} ${className}`.trim()}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      {passive ? (
        <span {...triggerProps}>
          <span>{label || term}</span>
          {!hideIcon ? <span className="hover-glossary-term__icon">i</span> : null}
        </span>
      ) : (
        <button {...triggerProps}>
          <span>{label || term}</span>
          {!hideIcon ? <span className="hover-glossary-term__icon">i</span> : null}
        </button>
      )}

      <span
        className="hover-glossary-term__card"
        role="tooltip"
        aria-hidden={!open}
        hidden={!open}
      >
        <strong>{entry.term}</strong>
        <span>{entry.meaning}</span>
        {entry.whyItMatters ? (
          <span className="hover-glossary-term__why">
            Why it matters: {entry.whyItMatters}
          </span>
        ) : null}
      </span>
    </span>
  );
}

HoverGlossaryTerm.propTypes = {
  term: PropTypes.string.isRequired,
  label: PropTypes.string,
  className: PropTypes.string,
  inline: PropTypes.bool,
  hideIcon: PropTypes.bool,
  passive: PropTypes.bool,
};

export default HoverGlossaryTerm;
