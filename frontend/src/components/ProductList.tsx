import type { ProductSummary } from "../types";
import { formatTl } from "../format";

interface Props {
  products: ProductSummary[];
  selected: string | null;
  compareIds: string[];
  onSelect: (id: string) => void;
  onToggleCompare: (id: string) => void;
}

export default function ProductList({ products, selected, compareIds, onSelect, onToggleCompare }: Props) {
  return (
    <ul className="product-list">
      {products.map((p) => (
        <li key={p.id} className={p.id === selected ? "product selected" : "product"}>
          <button className="product-main" onClick={() => onSelect(p.id)}>
            <span className={`score ${p.label}`}>{Math.round(p.score)}</span>
            <span className="product-text">
              <strong>{p.name}</strong>
              <span className="muted">
                {formatTl(p.price_tl)} · Enerji sınıfı {p.energy_class ?? "—"}
              </span>
            </span>
            <span className={`chip ${p.label}`}>{p.label_text}</span>
          </button>
          <label className="compare-toggle">
            <input
              id={`compare-${p.id}`}
              type="checkbox"
              checked={compareIds.includes(p.id)}
              onChange={() => onToggleCompare(p.id)}
            />
            Karşılaştır
          </label>
        </li>
      ))}
    </ul>
  );
}
