import { useEffect, useState } from "react";
import { api } from "./api";
import type { Category, ProductSummary } from "./types";
import ProductList from "./components/ProductList";
import ProductDetailPanel from "./components/ProductDetailPanel";
import WeightPanel from "./components/WeightPanel";
import CompareTable from "./components/CompareTable";

export default function App() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [category, setCategory] = useState<string | null>(null);
  const [products, setProducts] = useState<ProductSummary[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.categories()
      .then((cats) => {
        setCategories(cats);
        if (cats.length) setCategory(cats[0].id);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!category) return;
    setSelected(null);
    setCompareIds([]);
    api.products(category).then(setProducts).catch((e: Error) => setError(e.message));
  }, [category]);

  const current = categories.find((c) => c.id === category);

  const toggleCompare = (id: string) =>
    setCompareIds((ids) =>
      ids.includes(id) ? ids.filter((x) => x !== id) : ids.length < 4 ? [...ids, id] : ids,
    );

  return (
    <div className="app">
      <header className="top">
        <h1>GreenChoice</h1>
        <p>Ürünleri fiyatın yanında enerji, uzun vadeli maliyet ve dayanıklılığa göre karşılaştırın.</p>
        <nav className="tabs" aria-label="Kategoriler">
          {categories.map((c) => (
            <button
              key={c.id}
              className={c.id === category ? "tab active" : "tab"}
              onClick={() => setCategory(c.id)}
            >
              {c.name} <span className="muted">({c.product_count})</span>
            </button>
          ))}
        </nav>
      </header>

      {error && <div className="error">{error}</div>}

      {current && (
        <WeightPanel
          category={current}
          onScored={setProducts}
          onReset={() => api.products(current.id).then(setProducts)}
        />
      )}

      {compareIds.length >= 2 && (
        <CompareTable ids={compareIds} criteria={current?.criteria ?? []} />
      )}

      <main className="layout">
        <ProductList
          products={products}
          selected={selected}
          compareIds={compareIds}
          onSelect={setSelected}
          onToggleCompare={toggleCompare}
        />
        {selected ? (
          <ProductDetailPanel id={selected} criteria={current?.criteria ?? []} />
        ) : (
          <aside className="panel empty">Ayrıntıları ve skorun nedenlerini görmek için bir ürün seçin.</aside>
        )}
      </main>
    </div>
  );
}
