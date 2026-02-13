import { useMemo, useState } from 'react';
import { feedAPI } from '../services/api';
import { useFestivals } from '../hooks/useFestivals';
import './FeedSubscriptionsPage.css';

export function FeedSubscriptionsPage() {
    const [years, setYears] = useState(2);
    const [lang, setLang] = useState('en');
    const [selectedIds, setSelectedIds] = useState([]);
    const [copied, setCopied] = useState('');

    const { festivals, loading, error } = useFestivals();
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
        } catch {
            setCopied('');
        }
    }

    function toggleFestival(id) {
        setSelectedIds((current) => {
            if (current.includes(id)) return current.filter((v) => v !== id);
            return [...current, id];
        });
    }

    return (
        <section className="feeds-page">
            <header className="glass-card feeds-header">
                <div>
                    <h2 className="text-display">iCal Subscriptions</h2>
                    <p>Subscribe from Google Calendar, Apple Calendar, or Outlook with continuously updated festival dates.</p>
                </div>
                <div className="feeds-controls">
                    <label>
                        Years
                        <select value={years} onChange={(e) => setYears(Number(e.target.value))}>
                            {[1, 2, 3, 4, 5].map((v) => (
                                <option key={v} value={v}>{v}</option>
                            ))}
                        </select>
                    </label>

                    <label>
                        Language
                        <select value={lang} onChange={(e) => setLang(e.target.value)}>
                            <option value="en">English</option>
                            <option value="ne">Nepali</option>
                        </select>
                    </label>
                </div>
            </header>

            <section className="feeds-links-grid">
                {[
                    { key: 'all', title: 'All Festivals', link: quickLinks.all },
                    { key: 'national', title: 'National Holidays', link: quickLinks.national },
                    { key: 'newari', title: 'Newari Festivals', link: quickLinks.newari },
                ].map((item) => (
                    <article key={item.key} className="glass-card feed-card">
                        <h3>{item.title}</h3>
                        <p className="feed-link" title={item.link}>{item.link}</p>
                        <div className="feed-card__actions">
                            <a className="btn btn-primary" href={item.link} target="_blank" rel="noreferrer">Open Feed</a>
                            <button className="btn btn-secondary" onClick={() => copyLink(item.title, item.link)}>
                                {copied === item.title ? 'Copied' : 'Copy'}
                            </button>
                        </div>
                    </article>
                ))}
            </section>

            <section className="glass-card custom-feed">
                <div className="custom-feed__header">
                    <h3>Custom Festival Feed</h3>
                    <p>Select specific festivals to generate a focused iCal URL.</p>
                </div>

                <label className="custom-feed__search" htmlFor="festival-search">
                    <span>Search festivals</span>
                    <input
                        id="festival-search"
                        type="search"
                        placeholder="Dashain, Teej, Shivaratri"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                </label>

                {loading && <p>Loading festivals...</p>}
                {!loading && error && <p role="alert">{error}</p>}
                {!loading && !error && (
                    <div className="festival-picker" role="group" aria-label="Select festivals for custom feed">
                        {filtered.slice(0, 60).map((festival) => (
                            <label key={festival.id} className="picker-item">
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

                <div className="custom-feed__output">
                    <p><strong>Selected:</strong> {selectedIds.length}</p>
                    <p className="feed-link">{customLink || 'Select at least one festival to generate a custom link.'}</p>
                    {customLink && (
                        <div className="feed-card__actions">
                            <a className="btn btn-primary" href={customLink} target="_blank" rel="noreferrer">Open Custom Feed</a>
                            <button className="btn btn-secondary" onClick={() => copyLink('Custom', customLink)}>
                                {copied === 'Custom' ? 'Copied' : 'Copy'}
                            </button>
                        </div>
                    )}
                </div>
            </section>
        </section>
    );
}

export default FeedSubscriptionsPage;
