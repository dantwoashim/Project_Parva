import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { KundaliPage } from '../pages/KundaliPage';
import { MemberProvider } from '../context/MemberContext';

function response(payload) {
  return {
    ok: true,
    status: 200,
    statusText: 'OK',
    headers: { get: () => 'application/json' },
    json: async () => payload,
    text: async () => JSON.stringify(payload),
  };
}

describe('KundaliPage', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input) => {
        const url = String(input);

        if (url.includes('/places/search?')) {
          return response({
            query: 'Kathmandu',
            items: [
              {
                label: 'Kathmandu, Nepal',
                latitude: 27.7172,
                longitude: 85.324,
                timezone: 'Asia/Kathmandu',
                source: 'offline_nepal_gazetteer',
              },
            ],
            attribution: 'Offline gazetteer',
          });
        }

        if (url.includes('/kundali/graph')) {
          return response({
            data: {
              datetime: '1998-04-14T06:15:00',
              location: {
                latitude: 27.7172,
                longitude: 85.324,
                timezone: 'Asia/Kathmandu',
              },
              layout: {
                viewbox: '0 0 100 100',
                house_nodes: [
                  { id: 'house_1', house_number: 1, rashi_english: 'Aries', occupants: ['sun'], x: 10, y: 10 },
                  { id: 'house_2', house_number: 2, rashi_english: 'Taurus', occupants: [], x: 20, y: 20 },
                ],
                graha_nodes: [
                  { id: 'sun', x: 12, y: 12 },
                  { id: 'moon', x: 22, y: 22 },
                ],
                aspect_edges: [
                  { source: 'sun', target: 'moon' },
                ],
              },
              insight_blocks: [
                { id: 'lagna', title: 'Lagna', summary: 'Aries rising' },
              ],
              calculation_trace_id: 'tr_kundali_graph',
            },
            meta: {
              method: 'kundali_graph',
              confidence: { level: 'computed' },
            },
          });
        }

        if (url.includes('/kundali') && !url.includes('/kundali/graph') && !url.includes('/kundali/lagna')) {
          return response({
            method: 'kundali_profile',
            confidence: 'computed',
            calculation_trace_id: 'tr_kundali',
            lagna: { rashi_english: 'Aries' },
            grahas: {
              sun: {
                name_english: 'Sun',
                rashi_english: 'Aries',
                longitude: 10.5,
                dignity: { state: 'strong' },
              },
              moon: {
                name_english: 'Moon',
                rashi_english: 'Taurus',
                longitude: 22.1,
                dignity: { state: 'neutral' },
              },
            },
            houses: [
              { house_number: 1, rashi_english: 'Aries', occupants: ['sun'] },
              { house_number: 2, rashi_english: 'Taurus', occupants: ['moon'] },
            ],
            aspects: [
              { from: 'sun', to: 'moon', nature: 'trine', aspect_house: 5, aspect_angle: 120, strength: 0.8 },
            ],
          });
        }

        throw new Error(`Unhandled request in KundaliPage test: ${url}`);
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('searches for a place and generates a birth chart reading', async () => {
    render(
      <MemoryRouter>
        <MemberProvider>
          <KundaliPage />
        </MemberProvider>
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText(/^Day$/i), { target: { value: '14' } });
    fireEvent.change(screen.getByLabelText(/^Month$/i), { target: { value: '4' } });
    fireEvent.change(screen.getByLabelText(/^Year$/i), { target: { value: '1998' } });
    fireEvent.change(screen.getByLabelText(/^Birth time$/i), { target: { value: '06:15' } });
    fireEvent.change(screen.getByLabelText(/^Place$/i), { target: { value: 'Kathmandu' } });
    fireEvent.click(screen.getByRole('button', { name: /Search place/i }));
    fireEvent.click(await screen.findByRole('button', { name: /Kathmandu, Nepal/i }));
    fireEvent.click(screen.getByRole('button', { name: /Generate chart/i }));

    expect(await screen.findByText(/Generated chart/i, {}, { timeout: 10000 })).toBeInTheDocument();
    expect(screen.getByText(/Kathmandu, Nepal/i)).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Placements/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Aspects/i })).toBeInTheDocument();
  }, 10000);
});
