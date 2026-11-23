// Client-side search, filter and sort for the product list. Pure functions, no API calls:
// the list only rearranges what /api/products (or /api/score) returned.
import type { Label, ProductSummary } from "./types";

export type SortKey = "score" | "price_asc" | "price_desc" | "energy";

export interface ListFilter {
  query: string;
  energy: string; // "" = all classes
  label: Label | ""; // "" = all labels
  sort: SortKey;
}

export const DEFAULT_FILTER: ListFilter = { query: "", energy: "", label: "", sort: "score" };

// Display texts are in i18n (list.sortScore ...), keyed by these ids.
export const SORT_KEYS: SortKey[] = ["score", "price_asc", "price_desc", "energy"];

// Lower-case in Turkish and fold the Turkish letters, so "SIEMENS", "Siemens" and
// "siemens" match, and "camasir" finds "Çamaşır".
const FOLD: Record<string, string> = { ç: "c", ğ: "g", ı: "i", ö: "o", ş: "s", ü: "u" };
export const normalize = (s: string) =>
  s.toLocaleLowerCase("tr-TR").replace(/[çğıöşü]/g, (ch) => FOLD[ch]).trim();

const matchesQuery = (p: ProductSummary, query: string) => {
  const q = normalize(query);
  if (!q) return true;
  const haystack = normalize(`${p.name} ${p.brand ?? ""}`);
  return q.split(/\s+/).every((word) => haystack.includes(word));
};

// Missing values always go to the end, whatever the direction.
const compareNullable = (a: number | null, b: number | null, dir: 1 | -1) => {
  if (a == null && b == null) return 0;
  if (a == null) return 1;
  if (b == null) return -1;
  return (a - b) * dir;
};

// The 2021 EU scale runs A (best) to G. Any other value (for example an old "A++" that is
// still in the synthetic sample data) is not comparable with it and sorts with the unknowns.
const NEW_SCALE = "ABCDEFG";
const energyRank = (c: string | null) => {
  const k = c?.trim().toUpperCase() ?? "";
  return k.length === 1 && NEW_SCALE.includes(k) ? NEW_SCALE.indexOf(k) : null;
};

const comparators: Record<SortKey, (a: ProductSummary, b: ProductSummary) => number> = {
  score: (a, b) => b.score - a.score,
  price_asc: (a, b) => compareNullable(a.price_tl, b.price_tl, 1),
  price_desc: (a, b) => compareNullable(a.price_tl, b.price_tl, -1),
  energy: (a, b) => compareNullable(energyRank(a.energy_class), energyRank(b.energy_class), 1),
};

export function applyFilter(products: ProductSummary[], f: ListFilter): ProductSummary[] {
  const tie = comparators.score; // equal keys keep the score order
  return products
    .filter((p) => matchesQuery(p, f.query))
    .filter((p) => !f.energy || p.energy_class === f.energy)
    .filter((p) => !f.label || p.label === f.label)
    .sort((a, b) => comparators[f.sort](a, b) || tie(a, b));
}

// Options come from the data, so the UI never offers a class or label that has no product.
export const energyClasses = (products: ProductSummary[]) =>
  [...new Set(products.map((p) => p.energy_class).filter((c): c is string => !!c))].sort();

export const labelOptions = (products: ProductSummary[]): Label[] => {
  const present = new Set(products.map((p) => p.label));
  const order: Label[] = ["recommended", "neutral", "not_recommended"];
  return order.filter((l) => present.has(l));
};

export const isFiltered = (f: ListFilter) => !!(f.query.trim() || f.energy || f.label);
