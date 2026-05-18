import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import {
  Confidence,
  InfoCell,
  SourceDots,
  TimelineList,
  VerificationStrip,
} from '../redesign/components/VerificationComponents';
import { PanchangaProofDrawer } from '../proof/PanchangaProofDrawer';
import { ProofViewerPage } from '../proof/ProofViewerPage';

describe('verification component extraction', () => {
  it('renders clamped confidence and source dots', () => {
    render(
      <>
        <Confidence value={108} />
        <SourceDots active={3} />
      </>,
    );

    expect(screen.getByText('100%')).toBeInTheDocument();
    expect(screen.getByLabelText('3 of 6 source checks passed')).toBeInTheDocument();
  });

  it('renders verification strip and info cells', () => {
    render(
      <>
        <VerificationStrip items={[{ label: 'Policy', value: 'Public', meta: 'stable' }]} />
        <InfoCell icon="i" label="Trace" value="trace-1" meta="source aware" />
      </>,
    );

    expect(screen.getByLabelText('Verification summary')).toBeInTheDocument();
    expect(screen.getByText('Public')).toBeInTheDocument();
    expect(screen.getByText('trace-1')).toBeInTheDocument();
  });

  it('renders timeline links without depending on the god component', () => {
    render(
      <MemoryRouter>
        <TimelineList items={[{ time: '08:00', title: 'Good window', type: 'good', icon: '+' }]} />
      </MemoryRouter>,
    );

    expect(screen.getByRole('link', { name: /08:00/i })).toHaveAttribute('href', '/best-time');
  });

  it('renders Panchanga proof metadata and non-authority boundary', () => {
    render(
      <PanchangaProofDrawer
        proof={{
          capsule: {
            identity_hash: 'parva:id:v1:sha256:abc',
            witness_hash: 'parva:wit:v1:sha256:def',
            canonical_query: {
              context: {
                latitude: 27.7172,
                longitude: 85.324,
                timezone: 'Asia/Kathmandu',
                ayanamsa: 'lahiri',
              },
            },
            boundary: { claim_boundary: 'computed_ephemeris_not_panchanga_authority' },
            ephemeris_metadata: {
              provider_id: 'pinned_panchanga_fixture',
              provider_kind: 'pinned_fixture',
              ephemeris_version: 'fixture-v1',
            },
            result: {
              tithi: { name: 'Pratipada' },
              nakshatra: { name: 'Ashwini' },
            },
            field_provenance: {
              tithi: { authority: 'computed_uncertified' },
              nakshatra: { authority: 'computed_uncertified' },
            },
          },
        }}
      />,
    );

    expect(screen.getByRole('heading', { name: /Panchanga proof/i })).toBeInTheDocument();
    expect(screen.getByText(/not official Panchanga authority/i)).toBeInTheDocument();
    expect(screen.getByText(/pinned_panchanga_fixture/i)).toBeInTheDocument();
    expect(screen.getByText('computed_ephemeris_not_panchanga_authority')).toBeInTheDocument();
    expect(screen.getByText('Field provenance')).toBeInTheDocument();
  });

  it('renders the proof viewer without unsafe HTML execution', () => {
    render(<ProofViewerPage />);

    expect(screen.getByRole('heading', { name: /Inspect Parva proof packs and Timepacks/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/Artifact JSON/i)).toBeInTheDocument();
    expect(screen.getByText(/ready_for_offline_cli_replay/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Boundary vector/i)).toBeInTheDocument();
    expect(screen.getByText(/Not government, legal, tax, payroll, banking/i)).toBeInTheDocument();
  });
});
