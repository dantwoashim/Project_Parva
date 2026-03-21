import PropTypes from 'prop-types';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useDialogA11y } from '../../hooks/useDialogA11y';
import { AuthorityInspector } from './AuthorityInspector';
import { trackEvent } from '../../services/analytics';
import './EvidenceDrawer.css';

export function EvidenceDrawer({
  title,
  intro,
  methodRef,
  confidenceNote,
  placeUsed,
  computedForDate,
  availability = [],
  meta,
  traceFallbackId,
}) {
  const [open, setOpen] = useState(false);
  const { dialogRef } = useDialogA11y(open, () => setOpen(false));

  function handleOpen() {
    trackEvent('methodology_opened', { source: 'drawer', title });
    setOpen(true);
  }

  return (
    <>
      <button type="button" className="btn btn-secondary evidence-drawer__trigger" onClick={handleOpen}>
        How this was calculated
      </button>

      {open ? (
        <div className="evidence-drawer__overlay" role="presentation" onClick={() => setOpen(false)}>
          <aside
            ref={dialogRef}
            className="evidence-drawer"
            role="dialog"
            aria-modal="true"
            aria-labelledby="evidence-drawer-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="evidence-drawer__header">
              <div>
                <p className="evidence-drawer__eyebrow">Method available</p>
                <h2 id="evidence-drawer-title">{title}</h2>
                <p className="evidence-drawer__intro">{intro}</p>
              </div>
              <button
                type="button"
                className="evidence-drawer__close"
                data-dialog-initial-focus="true"
                onClick={() => setOpen(false)}
              >
                Close
              </button>
            </div>

            <div className="evidence-drawer__facts">
              <article className="evidence-drawer__fact">
                <span>Place used</span>
                <strong>{placeUsed}</strong>
              </article>
              <article className="evidence-drawer__fact">
                <span>Date used</span>
                <strong>{computedForDate}</strong>
              </article>
              <article className="evidence-drawer__fact">
                <span>Confidence note</span>
                <strong>{confidenceNote}</strong>
              </article>
              <article className="evidence-drawer__fact">
                <span>Method</span>
                <strong>{methodRef}</strong>
              </article>
            </div>

            {availability.length ? (
              <div className="evidence-drawer__availability">
                {availability.map((item) => (
                  <article key={item.label} className="evidence-drawer__availability-item">
                    <span>{item.label}</span>
                    <strong>{item.available ? 'Available' : 'Deferred'}</strong>
                    {item.note ? <p>{item.note}</p> : null}
                  </article>
                ))}
              </div>
            ) : null}

            <AuthorityInspector title={`${title} metadata`} meta={meta} traceFallbackId={traceFallbackId} />

            <div className="evidence-drawer__footer">
              <p>Open the full methodology page when you want the broader trust model, variance notes, and review expectations in one place.</p>
              <Link to="/methodology" className="btn btn-secondary" onClick={() => setOpen(false)}>
                Open methodology
              </Link>
            </div>
          </aside>
        </div>
      ) : null}
    </>
  );
}

EvidenceDrawer.propTypes = {
  title: PropTypes.string.isRequired,
  intro: PropTypes.string.isRequired,
  methodRef: PropTypes.string.isRequired,
  confidenceNote: PropTypes.string.isRequired,
  placeUsed: PropTypes.string.isRequired,
  computedForDate: PropTypes.string.isRequired,
  availability: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    available: PropTypes.bool.isRequired,
    note: PropTypes.string,
  })),
  meta: PropTypes.object,
  traceFallbackId: PropTypes.string,
};

EvidenceDrawer.defaultProps = {
  availability: [],
  meta: null,
  traceFallbackId: null,
};

export default EvidenceDrawer;
