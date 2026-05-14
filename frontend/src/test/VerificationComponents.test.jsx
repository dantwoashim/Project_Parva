import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import {
  Confidence,
  InfoCell,
  SourceDots,
  TimelineList,
  VerificationStrip,
} from '../redesign/components/VerificationComponents';

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
});
