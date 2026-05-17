export function BoundaryEmbed({ boundary }) {
  if (!boundary) {
    return null;
  }

  return (
    <aside aria-label="Claim boundary">
      <strong>{boundary.claim_boundary || boundary.claimBoundary}</strong>
      <span>Not government, legal, tax, banking, payroll, or religious authority.</span>
    </aside>
  );
}
