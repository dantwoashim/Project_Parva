import { fireEvent, render, screen } from '@testing-library/react';
import HoverGlossaryTerm from '../components/UI/HoverGlossaryTerm';

describe('HoverGlossaryTerm', () => {
  it('shows the info card only while hovered or focused', () => {
    render(<HoverGlossaryTerm term="Tithi" label="Tithi" />);

    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();

    fireEvent.mouseEnter(screen.getByRole('button', { name: /Tithi/i }));
    expect(screen.getByRole('tooltip')).toBeInTheDocument();

    fireEvent.mouseLeave(screen.getByRole('button', { name: /Tithi/i }));
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });
});
