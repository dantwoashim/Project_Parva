import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FestivalCard } from '../components/Festival';
import { useFestivals } from '../hooks/useFestivals';
import './FestivalExplorerPage.css';

const CATEGORY_OPTIONS = [
    { value: '', label: 'All Categories' },
    { value: 'national', label: 'National' },
    { value: 'newari', label: 'Newari' },
    { value: 'buddhist', label: 'Buddhist' },
    { value: 'hindu', label: 'Hindu' },
    { value: 'regional', label: 'Regional' },
];

const QUALITY_OPTIONS = [
    { value: 'computed', label: 'Computed' },
    { value: 'provisional', label: 'Provisional' },
    { value: 'inventory', label: 'Inventory' },
    { value: 'all', label: 'All Bands' },
];

function formatPct(value) {
    if (value === null || value === undefined) return '0.00%';
    const numeric = Number(value);
    if (Number.isNaN(numeric)) return '0.00%';
    return `${numeric.toFixed(2)}%`;
}

export function FestivalExplorerPage() {
    const navigate = useNavigate();
    const [search, setSearch] = useState('');
    const [category, setCategory] = useState('');
    const [sortBy, setSortBy] = useState('significance');
    const [qualityBand, setQualityBand] = useState('computed');
    const [algorithmicOnly, setAlgorithmicOnly] = useState(true);

    const { festivals, total, scoreboard, loading, error } = useFestivals({
        category,
        search,
        qualityBand,
        algorithmicOnly,
    });

    const sortedFestivals = useMemo(() => {
        const rows = [...festivals];
        if (sortBy === 'name') {
            rows.sort((a, b) => a.name.localeCompare(b.name));
        } else if (sortBy === 'duration') {
            rows.sort((a, b) => (b.duration_days || 0) - (a.duration_days || 0));
        } else {
            rows.sort((a, b) => (b.significance_level || 0) - (a.significance_level || 0));
        }
        return rows;
    }, [festivals, sortBy]);

    const computedCount = scoreboard?.computed?.count ?? 0;
    const provisionalCount = scoreboard?.provisional?.count ?? 0;
    const inventoryCount = scoreboard?.inventory?.count ?? 0;

    return (
        <section className="explorer-page">
            <header className="explorer-page__header glass-card motion-stagger">
                <div className="explorer-page__headline">
                    <p className="explorer-page__eyebrow">Authority Coverage • Headline = Computed</p>
                    <h1 className="text-display">Festival Explorer</h1>
                    <p>
                        Discover festivals with truth-first quality bands and computed-first headline metrics.
                    </p>
                </div>

                <div className="explorer-page__scoreboard" aria-label="Coverage scoreboard">
                    <article className="score-card score-card--computed interactive-surface">
                        <p className="score-card__label">Computed</p>
                        <p className="score-card__value">{computedCount}</p>
                        <p className="score-card__meta">{formatPct(scoreboard?.computed?.pct)}</p>
                    </article>
                    <article className="score-card score-card--provisional interactive-surface">
                        <p className="score-card__label">Provisional</p>
                        <p className="score-card__value">{provisionalCount}</p>
                        <p className="score-card__meta">{formatPct(scoreboard?.provisional?.pct)}</p>
                    </article>
                    <article className="score-card score-card--inventory interactive-surface">
                        <p className="score-card__label">Inventory</p>
                        <p className="score-card__value">{inventoryCount}</p>
                        <p className="score-card__meta">{formatPct(scoreboard?.inventory?.pct)}</p>
                    </article>
                    <article className="score-card score-card--claim interactive-surface">
                        <p className="score-card__label">Claim Guard</p>
                        <p className="score-card__value score-card__value--small">
                            {scoreboard?.claim_guard?.safe_to_claim_300 ? 'Ready' : 'In Progress'}
                        </p>
                        <p className="score-card__meta">Headline: computed</p>
                    </article>
                </div>
            </header>

            <section className="explorer-page__filters glass-card motion-stagger">
                <label className="filter-field filter-field--search">
                    <span>Search</span>
                    <input
                        type="search"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Dashain, Tihar, Shivaratri..."
                    />
                </label>

                <label className="filter-field">
                    <span>Category</span>
                    <select value={category} onChange={(e) => setCategory(e.target.value)}>
                        {CATEGORY_OPTIONS.map((option) => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                </label>

                <label className="filter-field">
                    <span>Quality Band</span>
                    <select value={qualityBand} onChange={(e) => setQualityBand(e.target.value)}>
                        {QUALITY_OPTIONS.map((option) => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                </label>

                <label className="filter-field">
                    <span>Sort</span>
                    <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                        <option value="significance">Significance</option>
                        <option value="name">Name</option>
                        <option value="duration">Duration</option>
                    </select>
                </label>

                <label className="filter-switch" htmlFor="algorithmic-only">
                    <input
                        id="algorithmic-only"
                        type="checkbox"
                        checked={algorithmicOnly}
                        onChange={(e) => setAlgorithmicOnly(e.target.checked)}
                    />
                    <span>Algorithmic only</span>
                </label>

                <div className="explorer-page__result-total" role="status" aria-live="polite">
                    {loading ? 'Loading…' : `${total} results`}
                </div>
            </section>

            {loading && (
                <div className="explorer-grid">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="explorer-skeleton skeleton" />
                    ))}
                </div>
            )}

            {!loading && error && (
                <div className="glass-card explorer-error motion-stagger" role="alert">
                    <h3>Could not load festivals</h3>
                    <p>{error}</p>
                </div>
            )}

            {!loading && !error && sortedFestivals.length === 0 && (
                <div className="glass-card explorer-empty motion-stagger">
                    <h3>No festivals match the current filters</h3>
                    <p>Try switching quality band to “All Bands” or disabling algorithmic-only.</p>
                </div>
            )}

            {!loading && !error && sortedFestivals.length > 0 && (
                <div className="explorer-grid">
                    {sortedFestivals.map((festival) => (
                        <FestivalCard
                            key={festival.id}
                            festival={{
                                ...festival,
                                next_start: festival.next_start || festival.next_occurrence,
                                next_end: festival.next_end || festival.next_occurrence,
                            }}
                            onClick={() => navigate(`/festivals/${festival.id}`)}
                        />
                    ))}
                </div>
            )}
        </section>
    );
}

export default FestivalExplorerPage;
