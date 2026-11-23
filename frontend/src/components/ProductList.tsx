import type { ProductSummary } from "../types";
import { useI18n } from "../i18n";
import EnergyBadge from "./EnergyBadge";

interface Props {
  products: ProductSummary[];
  selected: string | null;
  compareIds: string[];
  onSelect: (id: string) => void;
  onToggleCompare: (id: string) => void;
}

// The label is shown from its id (not label_text), so switching language needs no refetch.
export default function ProductList({ products, selected, compareIds, onSelect, onToggleCompare }: Props) {
  const { t, formatTl } = useI18n();
  return (
    <ul className="product-list">
      {products.map((p) => (
        <li key={p.id} className={p.id === selected ? "product selected" : "product"}>
          <button className="product-main" onClick={() => onSelect(p.id)}>
            <span className={`score ${p.label}`}>{Math.round(p.score)}</span>
            <span className="product-text">
              <strong>{p.name}</strong>
              <span className="muted">
                {formatTl(p.price_tl)} · {t.list.energyClass} <EnergyBadge value={p.energy_class} />
              </span>
            </span>
            <span className={`chip ${p.label}`}>{t.labels[p.label]}</span>
          </button>
          <label className="compare-toggle">
            <input
              id={`compare-${p.id}`}
              type="checkbox"
              checked={compareIds.includes(p.id)}
              onChange={() => onToggleCompare(p.id)}
            />
            {t.list.compare}
          </label>
        </li>
      ))}
    </ul>
  );
}
