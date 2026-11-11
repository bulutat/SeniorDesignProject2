import { useEffect, useState } from "react";
import { api } from "../api";
import type { Category, ProductSummary } from "../types";

interface Props {
  category: Category;
  onScored: (products: ProductSummary[]) => void;
  onReset: () => void;
}

// Each choice is a relative weight; the API scales the weights so that they sum to 1.
// "Not important" leaves the criterion out of the score.
export const LEVELS = [
  { id: "none", label: "Önemli değil", weight: 0 },
  { id: "normal", label: "Önemli", weight: 1 },
  { id: "high", label: "Çok önemli", weight: 2 },
] as const;
type Level = (typeof LEVELS)[number]["id"];

// Starting choices follow the category's default weights (0.20 and above count as "very important").
export const levelFor = (weight: number): Level => (weight >= 0.2 ? "high" : weight > 0 ? "normal" : "none");
const defaults = (c: Category) =>
  Object.fromEntries(c.criteria.map((k) => [k.id, levelFor(k.weight)])) as Record<string, Level>;
export const toWeights = (levels: Record<string, Level>) =>
  Object.fromEntries(
    Object.entries(levels).map(([id, level]) => [id, LEVELS.find((l) => l.id === level)!.weight]),
  );

export default function WeightPanel({ category, onScored, onReset }: Props) {
  const [levels, setLevels] = useState<Record<string, Level>>(defaults(category));

  useEffect(() => setLevels(defaults(category)), [category]);

  const nothingSelected = Object.values(levels).every((l) => l === "none");
  const apply = () => api.customScore(category.id, toWeights(levels)).then(onScored);
  const reset = () => {
    setLevels(defaults(category));
    onReset();
  };

  return (
    <details className="weights">
      <summary>Sizin için hangi kriter ne kadar önemli?</summary>
      <div className="weight-grid">
        {category.criteria.map((c) => (
          <fieldset key={c.id} className="level-group">
            <legend>{c.name}</legend>
            <div className="level-options">
              {LEVELS.map((l) => (
                <label key={l.id} className={levels[c.id] === l.id ? "chosen" : undefined}>
                  <input
                    type="radio"
                    name={`level-${c.id}`}
                    value={l.id}
                    checked={levels[c.id] === l.id}
                    onChange={() => setLevels({ ...levels, [c.id]: l.id })}
                  />
                  {l.label}
                </label>
              ))}
            </div>
          </fieldset>
        ))}
      </div>
      {nothingSelected && (
        <p className="weight-note">En az bir kriteri "Önemli" veya "Çok önemli" seçin.</p>
      )}
      <div className="weight-actions">
        <button onClick={apply} disabled={nothingSelected}>Yeniden sırala</button>
        <button className="secondary" onClick={reset}>Varsayılana dön</button>
      </div>
    </details>
  );
}
