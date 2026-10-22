import { useEffect, useState } from "react";
import { api } from "../api";
import type { Category, ProductSummary } from "../types";

interface Props {
  category: Category;
  onScored: (products: ProductSummary[]) => void;
  onReset: () => void;
}

const defaults = (c: Category) => Object.fromEntries(c.criteria.map((k) => [k.id, k.weight]));

export default function WeightPanel({ category, onScored, onReset }: Props) {
  const [weights, setWeights] = useState<Record<string, number>>(defaults(category));

  useEffect(() => setWeights(defaults(category)), [category]);

  const apply = () => api.customScore(category.id, weights).then(onScored);
  const reset = () => {
    setWeights(defaults(category));
    onReset();
  };

  return (
    <details className="weights">
      <summary>Kriterlerin önemini kendiniz ayarlayın</summary>
      <div className="weight-grid">
        {category.criteria.map((c) => (
          <label key={c.id} htmlFor={`w-${c.id}`}>
            <span>{c.name}</span>
            <input
              id={`w-${c.id}`}
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={weights[c.id] ?? 0}
              onChange={(e) => setWeights({ ...weights, [c.id]: Number(e.target.value) })}
            />
          </label>
        ))}
      </div>
      <div className="weight-actions">
        <button onClick={apply}>Yeniden sırala</button>
        <button className="secondary" onClick={reset}>Varsayılana dön</button>
      </div>
    </details>
  );
}
