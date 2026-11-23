import { energyRank } from "../compareBest";

// Energy class as a coloured arrow, styled after the A (dark green) to G (red) scale of the
// EU energy label. The colours approximate that scale; they are not the official print values.
// Classes outside A-G (an old "A++" in the sample data) get a neutral grey badge.
export default function EnergyBadge({ value }: { value: string | null }) {
  if (!value) return <span className="energy-badge none">—</span>;
  const rank = energyRank(value);
  const cls = rank == null ? "other" : `e${"abcdefg"[rank]}`;
  return <span className={`energy-badge ${cls}`}>{value}</span>;
}
