import {
  useState,
  Link,
  useParams,
  useFestivalDetail,
  readableCategory,
  AppChrome,
} from '../ExperienceCommon.jsx';
import {
  ArrowLeft,
  ArrowUpRight,
  CalendarPlus,
  Download,
} from 'lucide-react';

import {
  FestivalArtwork,
  resolveFestivalVisual,
  formatFestivalDateRange,
  formatBsDateRange,
  countdownText,
  sourceStrength,
  getDetailRituals,
  buildCalendarFeedUrl,
  buildFestivalEvidenceUrl,
} from './FestivalUtils.jsx';

function readableEvidenceValue(value, fallback) {
  const text = String(value || '').trim();
  if (!text || text.toLowerCase() === 'unknown') return fallback;
  return text.replaceAll('_', ' ');
}

export function RedesignFestivalDetail() {
  const { festivalId = 'dashain' } = useParams();
  const [tab, setTab] = useState('rituals');
  const {
    festival,
    dates,
    nearbyFestivals,
    completeness,
    meta,
    loading,
    error,
  } = useFestivalDetail(festivalId, 2026);
  const displayName = festival?.name || readableCategory(festivalId);
  const detailRow = {
    id: festivalId,
    name: displayName,
    displayName,
    category: festival?.category || 'observance',
    start_date: dates?.start_date,
    end_date: dates?.end_date,
    bs_start: dates?.bs_start,
    bs_end: dates?.bs_end,
    duration_days: festival?.duration_days,
    quality_band: dates?.confidence || meta?.quality_band,
    rule_status: completeness?.overall,
    regional_focus: festival?.regions || festival?.regional_focus || [],
    images: festival?.images || [],
    summary: festival?.tagline || festival?.description || festival?.mythology?.summary || 'Festival detail is being loaded from the Parva API.',
  };
  const visual = resolveFestivalVisual(detailRow);
  const source = sourceStrength(detailRow);
  const rituals = getDetailRituals({ festival });
  const related = Array.isArray(nearbyFestivals) ? nearbyFestivals : [];
  const tags = [
    readableCategory(detailRow.category),
    ...(Array.isArray(festival?.deities) ? festival.deities : []),
    ...(Array.isArray(detailRow.regional_focus) ? detailRow.regional_focus.slice(0, 2) : []),
  ].filter(Boolean).slice(0, 5);

  return (
    <AppChrome>
      <main className="page-shell detail-page">
        <div className="breadcrumb">
          <Link to="/festivals"><ArrowLeft aria-hidden="true" /> Back to festivals</Link>
          <span>/</span>
          <strong>{displayName}</strong>
        </div>

        {loading && !festival ? (
          <section className="panel festival-empty-state">
            <p className="eyebrow">Loading festival</p>
            <h1>Opening {displayName}.</h1>
            <p>The full detail route is fetching its source-aware profile from the API.</p>
          </section>
        ) : error ? (
          <section className="panel festival-empty-state">
            <p className="eyebrow">Detail unavailable</p>
            <h1>{displayName}</h1>
            <p>{error}</p>
            <Link className="primary-button" to="/festivals">Return to festival list</Link>
          </section>
        ) : (
          <>
        <section className={`detail-hero festival-detail-hero tone-${visual.tone}`}>
          <aside className="panel deity-card">
            <FestivalArtwork festival={detailRow} priority />
            <strong>{source.label}</strong>
          </aside>
          <section className="detail-title-block">
            <p className="eyebrow">{readableCategory(detailRow.category)}</p>
            <h1>{displayName}</h1>
            <p>{detailRow.summary}</p>
            <div className="detail-date-strip">
              <span><b>{formatBsDateRange(detailRow)}</b><small>Bikram Sambat</small></span>
              <span><b>{formatFestivalDateRange(dates?.start_date, dates?.end_date)}</b><small>Gregorian</small></span>
              <span><b>{source.score}%</b><small>Source confidence</small></span>
            </div>
            <div className="festival-tag-row">
              {tags.map((tag) => <span key={tag}>{tag}</span>)}
            </div>
          </section>
          <aside className="panel countdown-card">
            <p className="eyebrow">Starts in</p>
            <h2>{countdownText(dates?.start_date)}</h2>
            <p>{formatBsDateRange(detailRow)}</p>
            <a className="primary-button" href={buildCalendarFeedUrl(festivalId)}>
              <CalendarPlus aria-hidden="true" /> Add to calendar
            </a>
          </aside>
        </section>
        <section className="detail-workspace">
          <section className="panel detail-main">
            <div className="tab-row">
              {['rituals', 'meaning', 'calendar'].map((item) => (
                <button key={item} type="button" className={tab === item ? 'is-selected' : ''} onClick={() => setTab(item)}>{item}</button>
              ))}
            </div>
            <h2>{tab === 'rituals' ? 'Ritual sequence' : tab === 'meaning' ? 'Meaning and context' : 'Calendar window'}</h2>
            {tab === 'rituals' && (
              <>
                <p>{festival?.mythology?.significance || festival?.description || 'Structured ritual notes are loaded from the public festival profile when available.'}</p>
                <div className="ritual-list">
                  {(rituals.length ? rituals : [{ id: 'pending', day: 'API', title: 'Ritual notes pending', body: 'This observance is in the catalog, but detailed ritual sequencing is still being normalized.' }]).map((ritual, index) => (
                    <article key={ritual.id} className={index === 0 ? 'is-current' : ''}>
                      <span>0{index + 1}</span>
                      <div>
                        <strong>{ritual.title}</strong>
                        <p>{ritual.body}</p>
                      </div>
                      <time>{ritual.day}</time>
                    </article>
                  ))}
                </div>
              </>
            )}
            {tab === 'meaning' && (
              <div className="meaning-grid">
                <article>
                  <p className="eyebrow">Cultural meaning</p>
                  <h3>{festival?.mythology?.summary || 'Meaning profile'}</h3>
                  <p>{festival?.mythology?.significance || festival?.description || detailRow.summary}</p>
                </article>
                <article>
                  <p className="eyebrow">How Parva presents it</p>
                  <h3>Source-aware, not prescriptive</h3>
                  <p>The app separates public date confidence from local ritual practice so families and communities can still follow their trusted authority.</p>
                </article>
              </div>
            )}
            {tab === 'calendar' && (
              <div className="calendar-window-grid">
                <article>
                  <span>Primary date</span>
                  <strong>{formatBsDateRange(detailRow)}</strong>
                  <p>{formatFestivalDateRange(dates?.start_date, dates?.end_date)}</p>
                </article>
                <article>
                  <span>Source state</span>
                  <strong>{source.label}</strong>
                  <p>{dates?.calculation_method || 'Parva festival profile'}</p>
                </article>
                <article>
                  <span>Region</span>
                  <strong>{detailRow.regional_focus.length ? detailRow.regional_focus.join(', ') : 'Nepal-focused'}</strong>
                  <p>Regional practice may refine ritual time.</p>
                </article>
              </div>
            )}
          </section>
          <aside className="detail-rail">
            <section className="panel observance-note-panel">
              <p className="eyebrow">Observance notes</p>
              <h3>{detailRow.regional_focus.length ? detailRow.regional_focus.join(', ') : 'Nepal-focused'}</h3>
              <p>{detailRow.summary}</p>
              <Link to="/festivals">View all festivals</Link>
            </section>
            <section className="panel provenance-panel">
              <div className="panel-heading tight">
                <p className="eyebrow">Provenance</p>
                <strong>{source.label}</strong>
              </div>
            <p>{dates?.calculation_method || 'Resolved through the Parva festival endpoint and source metadata.'}</p>
            <a className="text-link" href={buildFestivalEvidenceUrl(detailRow)}>
              <Download aria-hidden="true" /> Export evidence capsule
            </a>
            {[
              {
                name: 'Method',
                note: readableEvidenceValue(
                  meta?.method || dates?.calculation_method,
                  'Festival date endpoint',
                ),
              },
              {
                name: 'Confidence level',
                note: readableEvidenceValue(
                  meta?.quality_band || dates?.confidence,
                  'Source-aware',
                ),
              },
              ].map((item) => (
                <article key={item.name}>
                  <div>
                    <strong>{item.name}</strong>
                    <p>{item.note}</p>
                  </div>
                </article>
              ))}
              <Link className="primary-button" to="/truth-lab">Open evidence</Link>
            </section>
            <section className="panel related-festivals-panel">
              <p className="eyebrow">Related observances</p>
              {related.length ? related.slice(0, 4).map((item) => (
                <Link key={item.id} to={`/festivals/${item.id}`}>
                  <FestivalArtwork festival={item} compact />
                  <span>
                    <strong>{item.name}</strong>
                    <small>{readableCategory(item.category)}</small>
                  </span>
                  <ArrowUpRight aria-hidden="true" />
                </Link>
              )) : <p className="festival-muted-note">No nearby observances were returned for this profile.</p>}
            </section>
          </aside>
        </section>
          </>
        )}
      </main>
    </AppChrome>
  );
}

