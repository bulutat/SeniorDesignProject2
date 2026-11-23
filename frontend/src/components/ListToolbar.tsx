import type { ProductSummary } from "../types";
import {
  DEFAULT_FILTER,
  SORT_OPTIONS,
  energyClasses,
  isFiltered,
  labelOptions,
  type ListFilter,
  type SortKey,
} from "../listView";

interface Props {
  products: ProductSummary[]; // the full list, before filtering
  shown: number;
  filter: ListFilter;
  onChange: (f: ListFilter) => void;
}

export default function ListToolbar({ products, shown, filter, onChange }: Props) {
  const set = (patch: Partial<ListFilter>) => onChange({ ...filter, ...patch });

  return (
    <div className="list-toolbar" role="search">
      <input
        type="search"
        className="search"
        placeholder="Ürün veya marka ara…"
        aria-label="Ürün veya marka ara"
        value={filter.query}
        onChange={(e) => set({ query: e.target.value })}
      />
      <div className="toolbar-row">
        <select
          aria-label="Enerji sınıfı"
          value={filter.energy}
          onChange={(e) => set({ energy: e.target.value })}
        >
          <option value="">Tüm enerji sınıfları</option>
          {energyClasses(products).map((c) => (
            <option key={c} value={c}>Enerji sınıfı {c}</option>
          ))}
        </select>
        <select
          aria-label="Öneri durumu"
          value={filter.label}
          onChange={(e) => set({ label: e.target.value as ListFilter["label"] })}
        >
          <option value="">Tüm öneriler</option>
          {labelOptions(products).map((l) => (
            <option key={l.id} value={l.id}>{l.text}</option>
          ))}
        </select>
        <select
          aria-label="Sıralama"
          value={filter.sort}
          onChange={(e) => set({ sort: e.target.value as SortKey })}
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.id} value={o.id}>{o.label}</option>
          ))}
        </select>
      </div>
      <p className="toolbar-count muted small" aria-live="polite">
        {shown} / {products.length} ürün
        {isFiltered(filter) && (
          <button className="link" onClick={() => onChange({ ...DEFAULT_FILTER, sort: filter.sort })}>
            Filtreleri temizle
          </button>
        )}
      </p>
    </div>
  );
}
