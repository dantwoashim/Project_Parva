import { useMemo, useState } from 'react';
import { feedAPI } from '../services/api';
import { useFestivals } from '../hooks/useFestivals';
import './FeedSubscriptionsPage.css';

export function FeedSubscriptionsPage() {
    const [years, setYears] = useState(2);
    const [lang, setLang] = useState('en');
    const [selectedIds, setSelectedIds] = useState([]);
    const [copied, setCopied] = useState('');

    const { festivals, loading, error } = useFestivals({ qualityBand: "all", algorithmicOnly: false });
    const [query, setQuery] = useState('');

    const filtered = useMemo(() => {
        const q = query.trim().toLowerCase();
        if (!q) return festivals;
        return festivals.filter((f) => `${f.name} ${f.name_nepali || ''}`.toLowerCase().includes(q));
    }, [festivals, query]);

    const customLink = useMemo(() => {
        if (!selectedIds.length) return '';
        return feedAPI.getCustomLink(selectedIds, years, lang);
    }, [selectedIds, years, lang]);

    const quickLinks = useMemo(() => ({
        all: feedAPI.getAllLink(years, lang),
        national: feedAPI.getNationalLink(years, lang),
        newari: feedAPI.getNewariLink(years, lang),
    }), [years, lang]);

    async function copyLink(label, link) {
        if (!link) return;
        try {
            await navigator.clipboard.writeText(link);
            setCopied(label);
            setTimeout(() => setCopied(''), 1500);
        } catch { setCopied(''); }
    }

    function toggleFestival(id) {
        setSelectedIds((current) => {
            if (current.includes(id)) return current.filter((v) => v !== id);
            return [...current, id];
        });
    }

    const FEED_CARDS = [
        { key: 'all', title: 'All Festivals', desc: 'Every festival computed by the engine', link: quickLinks.all, accent: 'gold' },
        { key: 'national', title: 'National Holidays', desc: 'Official government-declared holidays', link: quickLinks.national, accent: 'vermillion' },
        { key: 'newari', title: 'Newari Festivals', desc: 'Traditional Newar community observances', link: quickLinks.newari, accent: 'amber' },
    ];

    return (
        <section className="feeds-page animate-fade-in-up">
            <header className="feeds-hero">
                <h1 className="text-hero">Calendar Feeds</h1>
                <p className="feeds-hero__sub">
                    Subscribe from Google Calendar, Apple Calendar, or Outlook
                </p>
                <div className="feeds-hero__controls">
                    <label className="ink-input">
                        <span>Years</span>
                        <select value={years} onChange={(e) => setYears(Number(e.target.value))}>
                            {[1, 2, 3, 4, 5].map((v) => (
                                <option key={v} value={v}>{v}</option>
                            ))}
                        </select>
                    </label>
                    <label className="ink-input">
                        <span>Language</span>
                        <select value={lang} onChange={(e) => setLang(e.target.value)}>
                            <option value="en">English</option>
                            <option value="ne">Nepali</option>
                        </select>
                    </label>
                </div>
            </header>

            {/* Quick Feed Cards */}
            <section className="feeds-grid stagger-children">
                {FEED_CARDS.map((item) => (
                    <article key={item.key} className={`ink-card ink-card--${item.accent} feed-card`}>
                        <h3>{item.title}</h3>
                        <p className="feed-card__desc">{item.desc}</p>
                        <div className="feed-card__url">
                            <code>{item.link}</code>
                        </div>
                        <div className="feed-card__actions">
                            <a className="btn btn-primary btn-sm" href={item.link} target="_blank" rel="noreferrer">
                                Open Feed
                            </a>
                            <button className="btn btn-secondary btn-sm" onClick={() => copyLink(item.title, item.link)}>
                                {copied === item.title ? '✓ Copied' : 'Copy Link'}
                            </button>
                        </div>
                    </article>
                ))}
            </section>

            {/* Custom Feed Builder */}
            <section className="ink-card feeds-custom">
                <div className="feeds-custom__header">
                    <h3>Custom Festival Feed</h3>
                    <p>Select specific festivals to create a focused calendar feed.</p>
                </div>

                <div className="feeds-custom__search ink-input">
                    <span>Search</span>
                    <input
                        type="search"
                        placeholder="Dashain, Teej, Shivaratri..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                </div>

                {loading && <p className="feeds-custom__status">Loading festivals...</p>}
                {!loading && error && <p className="feeds-custom__status" role="alert">{error}</p>}
                {!loading && !error && (
                    <div className="feeds-picker">
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
                )}

                <div className="feeds-custom__output">
                    <p><strong>Selected:</strong> {selectedIds.length} festivals</p>
                    {customLink ? (
                        <>
                            <div className="feed-card__url"><code>{customLink}</code></div>
                            <div className="feed-card__actions">
                                <a className="btn btn-primary btn-sm" href={customLink} target="_blank" rel="noreferrer">Open Feed</a>
                                <button className="btn btn-secondary btn-sm" onClick={() => copyLink('Custom', customLink)}>
                                    {copied === 'Custom' ? '✓ Copied' : 'Copy Link'}
                                </button>
                            </div>
                        </>
                    ) : (
                        <p className="feeds-custom__hint">Select at least one festival above</p>
                    )}
                </div>
            </section>
        </section>
    );
}

export default FeedSubscriptionsPage;
