import PropTypes from 'prop-types';
import './MemberNoticeBar.css';

export function MemberNoticeBar({ notice, onDismiss }) {
  if (!notice) return null;

  return (
    <aside className="member-notice" role="status" aria-live="polite">
      <div className="member-notice__copy">
        <span className="member-notice__eyebrow">Saved state</span>
        <strong>{notice.title}</strong>
        <p>{notice.body}</p>
      </div>
      <button type="button" className="btn btn-secondary btn-sm" onClick={onDismiss}>
        Dismiss
      </button>
    </aside>
  );
}

MemberNoticeBar.propTypes = {
  notice: PropTypes.shape({
    title: PropTypes.string,
    body: PropTypes.string,
  }),
  onDismiss: PropTypes.func.isRequired,
};

MemberNoticeBar.defaultProps = {
  notice: null,
};

export default MemberNoticeBar;
