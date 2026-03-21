import { useMemo, useState } from 'react';
import { UtilityPageHeader } from '../consumer/UtilityPages';
import { feedAPI } from '../services/api';
import { useFestivals } from '../hooks/useFestivals';
import { useMemberContext } from '../context/useMemberContext';
import './FeedSubscriptionsPage.css';

function FeedCard({ title, desc, actionLabel, platform, link, copied, onCopy, onConnect }) {
  return (
    <article className="ink-card feed-card">
      <div className="feed-card__copy">
        <span className="feeds-page__eyebrow">Ready to connect</span>
        <h2>{title}</h2>
        <p>{desc}</p>
      </div>
      <div className="feed-card__actions">
        <button type="button" className="btn btn-primary btn-sm" onClick={() => onConnect(platform, title, link)}>
          {actionLabel}
        </button>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => onCopy(title, link)}>
          {copied === title ? 'Copied' : 'Copy link'}
        </button>
      </div>
      <details className="feed-card__advanced">
        <summary>Advanced manual setup</summary>
        <label className="ink-input feed-card__advanced-field">
          <span>Manual calendar link</span>
          <input readOnly value={link} onFocus={(event) => event.target.select()} />
        </label>
      </details>
    </article>
  );
}

export function FeedSubscriptionsPage() {
  const { startIntegration } = useMemberContext();
  const [years, setYears] = useState(2);
  const [lang, setLang] = useState('en');
  const [selectedIds, setSelectedIds] = useState([]);
  const [copied, setCopied] = useState('');
  const [query, setQuery] = useState('');

  const { festivals, loading, error } = useFestivals({ qualityBand: 'all', algorithmicOnly: false });

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return festivals;
    return festivals.filter((festival) => `${festival.name} ${festival.name_nepali || ''}`.toLowerCase().includes(normalized));
  }, [festivals, query]);

  const customLink = useMemo(() => {
    if (!selectedIds.length) return '';
    return feedAPI.getCustomLink(selectedIds, years, lang);
  }, [selectedIds, years, lang]);

  const feedCards = useMemo(() => ([
    {
      key: 'google',
      title: 'Google Calendar',
      desc: 'Add the broad Nepal-focused festival calendar to Google Calendar in one step.',
      actionLabel: 'Add to Google Calendar',
      platform: 'google',
      link: feedAPI.getAllLink(years, lang),
    },
    {
      key: 'apple',
      title: 'Apple Calendar',
      desc: 'Use the same calendar feed with Apple Calendar or any app that supports calendar subscriptions.',
      actionLabel: 'Add to Apple Calendar',
      platform: 'apple',
      link: feedAPI.getNationalLink(years, lang),
    },
    {
      key: 'manual',
      title: 'Manual setup',
      desc: 'Keep a direct calendar link for advanced manual setup or smaller custom integrations.',
      actionLabel: 'Open manual setup',
      platform: 'manual',
      link: feedAPI.getNewariLink(years, lang),
    },
  ]), [lang, years]);

  async function copyLink(label, link) {
    if (!link) return;
    try {
      await navigator.clipboard.writeText(link);
      setCopied(label);
      setTimeout(() => setCopied(''), 1500);
    } catch {
      setCopied('');
    }
  }

  function toggleFestival(id) {
    setSelectedIds((current) => {
      if (current.includes(id)) {
        return current.filter((value) => value !== id);
      }
      return [...current, id];
    });
  }

  async function handleIntegration(platform, title, link) {
    const allowed = await startIntegration({
      id: platform,
      platform,
      title,
      link,
      createdAt: new Date().toISOString(),
    });

    if (allowed) {
      if (typeof window.open === 'function') {
        window.open(link, '_blank', 'noreferrer');
      }
    }
  }

  return (
    <section className="feeds-page utility-page animate-fade-in-up">
      <UtilityPageHeader
        eyebrow="Calendar integrations"
        title="Connect Parva without dealing with raw calendar plumbing first."
        body="Choose a guided calendar setup first, then drop into manual setup only when you really need the direct link."
        links={[
          { label: 'Saved', to: '/#saved' },
          { label: 'Profile', to: '/profile' },
          { label: 'Methodology', to: '/methodology' },
        ]}
        aside={(
          <div className="feeds-hero__controls">
            <label className="ink-input">
              <span>Years</span>
              <select value={years} onChange={(event) => setYears(Number(event.target.value))}>
                {[1, 2, 3, 4, 5].map((value) => (
                  <option key={value} value={value}>{value}</option>
                ))}
              </select>
            </label>
            <label className="ink-input">
              <span>Language</span>
              <select value={lang} onChange={(event) => setLang(event.target.value)}>
                <option value="en">English</option>
                <option value="ne">Nepali</option>
              </select>
            </label>
          </div>
        )}
      />

      <section className="feeds-grid stagger-children">
        {feedCards.map((item) => (
          <FeedCard
            key={item.key}
            title={item.title}
            desc={item.desc}
            actionLabel={item.actionLabel}
            platform={item.platform}
            link={item.link}
            copied={copied}
            onCopy={copyLink}
            onConnect={handleIntegration}
          />
        ))}
      </section>

      <section className="ink-card feeds-custom utility-page__panel">
        <div className="feeds-custom__header">
          <div>
            <p className="feeds-page__eyebrow">Build your own</p>
            <h2>Make a smaller calendar for the observances you follow closely.</h2>
          </div>
          <p>Select the observances you want, then add the link to the calendar tool you already use.</p>
        </div>

        <label className="ink-input feeds-custom__search">
          <span>Search festivals</span>
          <input
            type="search"
            placeholder="Dashain, Teej, Shivaratri..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>

        {loading ? <p className="feeds-custom__status">Loading festivals...</p> : null}
        {!loading && error ? <p className="feeds-custom__status" role="alert">{error}</p> : null}
        {!loading && !error ? (
          <div className="feeds-picker" role="group" aria-label="Festival selector">
            {filtered.slice(0, 60).map((festival) => (
              <label key={festival.id} className="feeds-picker__item">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(festival.id)}
                  onChange={() => toggleFestival(festival.id)}
                />
                <span>{festival.name}</span>
              </label>
            ))}
          </div>
        ) : null}

        <div className="feeds-custom__output">
          <div className="feeds-custom__summary">
            <span>Selected festivals</span>
            <strong>{selectedIds.length}</strong>
          </div>

          {customLink ? (
            <div className="feeds-custom__actions">
              <button type="button" className="btn btn-primary btn-sm" onClick={() => handleIntegration('custom', 'Custom calendar', customLink)}>
                Add custom calendar
              </button>
              <button type="button" className="btn btn-secondary btn-sm" onClick={() => copyLink('Custom feed', customLink)}>
                {copied === 'Custom feed' ? 'Copied' : 'Copy link'}
              </button>
              <details className="feed-card__advanced feed-card__advanced--custom">
                <summary>Advanced manual setup</summary>
                <label className="ink-input feed-card__advanced-field">
                  <span>Manual calendar link</span>
                  <input readOnly value={customLink} onFocus={(event) => event.target.select()} />
                </label>
              </details>
            </div>
          ) : (
            <p className="feeds-custom__hint">Select at least one festival above to generate a custom feed.</p>
          )}
        </div>
      </section>
    </section>
  );
}

export const IntegrationsPage = FeedSubscriptionsPage;

export default FeedSubscriptionsPage;
