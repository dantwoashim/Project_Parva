import { verifyMembrane } from './membranes.js';

export function verifyStaticCard(card: { claim_boundary?: string; verified?: boolean }) {
  return card.verified === true && typeof card.claim_boundary === 'string';
}

export { verifyMembrane };
