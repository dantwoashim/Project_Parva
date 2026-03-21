import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import './UtilityPages.css';

function UtilityLinkRail({ links }) {
  if (!links?.length) return null;

  return (
    <nav className="utility-page__rail" aria-label="Secondary navigation">
      {links.map((item) => (
        <Link key={`${item.to}-${item.label}`} className="utility-page__rail-link" to={item.to}>
          {item.label}
        </Link>
      ))}
    </nav>
  );
}

UtilityLinkRail.propTypes = {
  links: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    to: PropTypes.string.isRequired,
  })),
};

UtilityLinkRail.defaultProps = {
  links: [],
};

export function UtilityPageHeader({
  eyebrow,
  title,
  body,
  aside,
  links,
}) {
  return (
    <header className="utility-page__hero editorial-card">
      <div className="utility-page__hero-copy">
        <p className="utility-page__eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="utility-page__lede">{body}</p>
        <UtilityLinkRail links={links} />
      </div>
      {aside ? <div className="utility-page__aside">{aside}</div> : null}
    </header>
  );
}

UtilityPageHeader.propTypes = {
  eyebrow: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  body: PropTypes.string.isRequired,
  aside: PropTypes.node,
  links: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    to: PropTypes.string.isRequired,
  })),
};

UtilityPageHeader.defaultProps = {
  aside: null,
  links: [],
};

export function UtilityStatGrid({ items }) {
  if (!items?.length) return null;

  return (
    <section className="utility-page__stats">
      {items.map((item) => (
        <article key={item.label} className="ink-card utility-page__stat">
          <span>{item.label}</span>
          <strong>{item.value}</strong>
        </article>
      ))}
    </section>
  );
}

UtilityStatGrid.propTypes = {
  items: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  })),
};

UtilityStatGrid.defaultProps = {
  items: [],
};

export default UtilityPageHeader;
