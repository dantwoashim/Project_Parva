export function TimelineCanvas({ items = [] }: { items?: Array<{ label: string }> }) {
  return (
    <ol aria-label="Parva timeline">
      {items.map((item) => (
        <li key={item.label}>{item.label}</li>
      ))}
    </ol>
  );
}
