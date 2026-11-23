import type { ProductSummary } from "../types";
import { useI18n } from "../i18n";
import type { Messages } from "../i18n/tr";
import {
  DEFAULT_FILTER,
  SORT_KEYS,
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

const sortText = (t: Messages, k: SortKey) =>
  ({ score: t.list.sortScore, price_asc: t.list.sortPriceAsc, price_desc: t.list.sortPriceDesc,
     energy: t.list.sortEnergy })[k];

export default function ListToolbar({ products, shown, filter, onChange }: Props) {
  const { t } = useI18n();
  const set = (patch: Partial<ListFilter>) => onChange({ ...filter, ...patch });

  return (
    <div className="list-toolbar" role="search">
      <input
        type="search"
        className="search"
        placeholder={t.list.search}
        aria-label={t.list.search}
        value={filter.query}
        onChange={(e) => set({ query: e.target.value })}
      />
      <div className="toolbar-row">
        <select
          aria-label={t.list.energyFilter}
          value={filter.energy}
          onChange={(e) => set({ energy: e.target.value })}
        >
          <option value="">{t.list.allEnergy}</option>
          {energyClasses(products).map((c) => (
            <option key={c} value={c}>{t.list.energyOption(c)}</option>
          ))}
        </select>
        <select
          aria-label={t.list.labelFilter}
          value={filter.label}
          onChange={(e) => set({ label: e.target.value as ListFilter["label"] })}
        >
          <option value="">{t.list.allLabels}</option>
          {labelOptions(products).map((l) => (
            <option key={l} value={l}>{t.labels[l]}</option>
          ))}
        </select>
        <select
          aria-label={t.list.sort}
          value={filter.sort}
          onChange={(e) => set({ sort: e.target.value as SortKey })}
        >
          {SORT_KEYS.map((k) => (
            <option key={k} value={k}>{sortText(t, k)}</option>
          ))}
        </select>
      </div>
      <p className="toolbar-count muted small" aria-live="polite">
        {t.list.count(shown, products.length)}
        {isFiltered(filter) && (
          <button className="link" onClick={() => onChange({ ...DEFAULT_FILTER, sort: filter.sort })}>
            {t.list.clear}
          </button>
        )}
      </p>
    </div>
  );
}
