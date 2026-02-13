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

export function FestivalExplorerPage() {
    const navigate = useNavigate();
    const [search, setSearch] = useState('');
    const [category, setCategory] = useState('');
    const [sortBy, setSortBy] = useState('significance');

    const { festivals, total, loading, error } = useFestivals({ category, search });

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

    return (
        <section className="explorer-page">
            <header className="explorer-page__header glass-card">
                <div>
                    <h1 className="text-display">Festival Explorer</h1>
                    <p>Search, filter, and sort Nepal&apos;s festival dataset.</p>
                </div>
                <div className="explorer-page__stats">
                    <span className="badge">{total} festivals</span>
                </div>
            </header>

            <section className="explorer-page__filters glass-card">
                <label className="filter-field">
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
                    <span>Sort</span>
                    <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                        <option value="significance">Significance</option>
                        <option value="name">Name</option>
                        <option value="duration">Duration</option>
                    </select>
                </label>
            </section>

            {loading && (
                <div className="explorer-grid">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="explorer-skeleton skeleton" />
                    ))}
                </div>
            )}

            {!loading && error && (
                <div className="glass-card explorer-error">
                    <h3>Could not load festivals</h3>
                    <p>{error}</p>
                </div>
            )}

            {!loading && !error && (
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
