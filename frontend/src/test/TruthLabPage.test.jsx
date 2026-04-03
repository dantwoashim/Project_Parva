import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { TruthLabPage } from '../pages/TruthLabPage';

function response(payload) {
  return {
    ok: true,
    status: 200,
    statusText: 'OK',
    json: async () => payload,
    text: async () => JSON.stringify(payload),
  };
}

describe('TruthLabPage', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input) => {
        const url = String(input);
        if (url.includes('/festivals/disputes?')) {
          return response({
            year: 2026,
            total_items: 1,
            truth_ladder: [
              { tier: 'authoritative', title: 'Authoritative', body: 'Authority-backed.' },
              { tier: 'conflicted', title: 'Conflicted', body: 'Multiple candidates.' },
            ],
            disputes: [
              {
                festival_id: 'ghode-jatra',
                festival_name: 'Ghode Jatra',
                year: 2026,
                start_date: '2026-03-18',
                support_tier: 'conflicted',
                selection_policy: 'authority_compare',
                authority_conflict: true,
                alternate_candidates: [{ start: '2026-03-17', source_family: 'published_holiday_listing' }],
                boundary_radar: 'high_disagreement_risk',
                stability_score: 0.42,
                recommended_action: 'Compare authority-backed candidates before relying on a single date.',
                engine_path: 'override',
                fallback_used: false,
              },
            ],
            provenance: {},
          });
        }
        if (url.includes('/reliability/benchmark-manifest')) {
          return response({
            benchmark: {
              evaluation_track: 'override_assisted_practical',
              case_count: 103,
              pass_rate: 100,
              conflict_policy: 'public_default_selection_with_visible_alternates',
              abstention_policy: 'strict_mode_abstains_on_high_disagreement_risk',
              report_hash: 'abcdef1234567890',
              engine_manifest_hash: 'fedcba0987654321',
              source_hashes: {
                baseline_2080_2082: '1111222233334444',
              },
              known_limits: [
                'Boundary-sensitive observances can still show one-day disagreement near sunrise and lunar transitions.',
              ],
            },
            policy: {},
          });
        }
        if (url.includes('/reliability/differential-manifest')) {
          return response({
            differential: {
              total_compared: 3,
              drift_percent: 0,
              taxonomy: {
                agreement: 3,
                minor_difference: 0,
                major_difference: 0,
                source_missing: 0,
                incomparable: 0,
              },
              gate: {
                passed: true,
                major_count: 0,
              },
              known_limits: [
                'Differential analysis is only as broad as the current benchmark report pair.',
              ],
            },
            policy: {},
          });
        }
        if (url.includes('/reliability/source-review-queue')) {
          return response({
            queue: {
              total_items: 4,
              summary: {
                critical: 0,
                high: 2,
                medium: 2,
                ready_for_promotion: 1,
              },
              items: [
                {
                  source_id: 'moha_official_2076',
                  review_action: 'improve_extraction',
                  review_priority: 'high',
                },
                {
                  source_id: 'moha_official_2082',
                  review_action: 'review_and_promote',
                  review_priority: 'medium',
                },
              ],
            },
            policy: {},
          });
        }
        if (url.includes('/reliability/boundary-suite')) {
          return response({
            boundary_suite: {
              suite_count: 3,
              total_samples: 86,
              total_passed: 86,
              pass_rate: 1,
              suites: [
                { suite_id: 'tithi_boundaries_30', samples: 30, pass_rate: 1 },
                { suite_id: 'sankranti_24', samples: 24, pass_rate: 1 },
                { suite_id: 'adhik_maas_reference', samples: 32, pass_rate: 1 },
              ],
            },
            policy: {},
          });
        }
        if (url.includes('/festivals/ghode-jatra/proof-capsule?')) {
          return response({
            festival_id: 'ghode-jatra',
            festival_name: 'Ghode Jatra',
            year: 2026,
            request: { festival_id: 'ghode-jatra', year: 2026, authority_mode: 'authority_compare', risk_mode: 'strict' },
            selection: {
              start_date: '2026-03-18',
              support_tier: 'conflicted',
              engine_path: 'override',
              fallback_used: false,
            },
            source_lineage: {
              source_family: 'moha_pdf_2083',
              authority_conflict: true,
              rule_summary: 'Fallback legacy rule',
            },
            risk: {
              boundary_radar: 'high_disagreement_risk',
              stability_score: 0.42,
              risk_mode: 'strict',
              recommended_action: 'Compare authority-backed candidates before relying on a single date.',
              truth_ladder: [],
            },
            provenance: {},
          });
        }
        return response({});
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('renders the dispute atlas and proof capsule', async () => {
    render(
      <MemoryRouter initialEntries={['/truth-lab']}>
        <Routes>
          <Route path="/truth-lab" element={<TruthLabPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText(/Disagreement, proof, and boundary risk should be inspectable/i, {}, { timeout: 15000 })).toBeInTheDocument();
    expect(await screen.findByText(/Run metadata, hashes, and known limits stay attached to the score/i, {}, { timeout: 15000 })).toBeInTheDocument();
    expect(await screen.findByText(/Regression drift is tracked separately from authority-backed evaluation/i, {}, { timeout: 15000 })).toBeInTheDocument();
    expect(await screen.findByText(/Official-source inventory now feeds a deterministic human-review queue/i, {}, { timeout: 15000 })).toBeInTheDocument();
    expect(await screen.findByText(/Sunrise flips, sankranti edges, and adhik-month transitions stay regression-tested/i, {}, { timeout: 15000 })).toBeInTheDocument();
    expect(await screen.findByText(/Truth ladder/i, {}, { timeout: 15000 })).toBeInTheDocument();
    expect((await screen.findAllByText(/Ghode Jatra/i)).length).toBeGreaterThan(0);
    expect((await screen.findAllByText(/high disagreement risk/i)).length).toBeGreaterThan(0);
    expect((await screen.findAllByText(/Compare authority-backed candidates/i)).length).toBeGreaterThan(0);
  }, 15000);
});
