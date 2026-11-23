import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiError, api } from "./api";
import { useI18n } from "./i18n";
import LanguageSelect from "./components/LanguageSelect";
import type { Category, ProductSummary } from "./types";
import ProductList from "./components/ProductList";
import ProductDetailPanel from "./components/ProductDetailPanel";
import WeightPanel from "./components/WeightPanel";
import CompareTable from "./components/CompareTable";
import ListToolbar from "./components/ListToolbar";
import GuideDrawer from "./components/GuideDrawer";
import type { GuideTab } from "./components/guide/sections";
import { DEFAULT_FILTER, applyFilter, type ListFilter } from "./listView";

export default function App() {
  const { lang, t } = useI18n();
  const [categories, setCategories] = useState<Category[]>([]);
  const [category, setCategory] = useState<string | null>(null);
  const [products, setProducts] = useState<ProductSummary[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [filter, setFilter] = useState<ListFilter>(DEFAULT_FILTER);
  const [guideTab, setGuideTab] = useState<GuideTab | null>(null); // null = guide closed
  const closeGuide = useCallback(() => setGuideTab(null), []);

  // Reloaded on a language change for the translated category and criterion names.
  // The selected category, filters, comparison and custom weights stay as they are.
  useEffect(() => {
    api.categories(lang)
      .then((cats) => {
        setCategories(cats);
        setCategory((cur) => cur ?? cats[0]?.id ?? null);
      })
      .catch(setError);
  }, [lang]);

  // Not reloaded on a language change: the list shows labels from their id, and a reload
  // would drop scores re-ranked with custom weights.
  useEffect(() => {
    if (!category) return;
    setSelected(null);
    setCompareIds([]);
    setFilter(DEFAULT_FILTER);
    api.products(category, lang).then(setProducts).catch(setError);
  }, [category]);

  // The API's own message is Turkish, so it is shown only in Turkish.
  const errorText =
    error instanceof ApiError
      ? lang === "tr" && error.detail ? error.detail : t.app.requestFailed(error.status)
      : error instanceof Error ? error.message : null;

  const current = categories.find((c) => c.id === category);
  const visible = useMemo(() => applyFilter(products, filter), [products, filter]);

  const toggleCompare = (id: string) =>
    setCompareIds((ids) =>
      ids.includes(id) ? ids.filter((x) => x !== id) : ids.length < 4 ? [...ids, id] : ids,
    );

  return (
    <div className="app">
      <header className="top">
        <div className="top-row">
          <h1>GreenChoice</h1>
          <div className="top-actions">
            <LanguageSelect />
            <button className="help-button" onClick={() => setGuideTab("start")}>
              <span className="help-icon" aria-hidden="true">?</span> {t.app.help}
            </button>
          </div>
        </div>
        <p>{t.app.subtitle}</p>
        <nav className="tabs" aria-label={t.app.categoriesNav}>
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

      {errorText && <div className="error">{errorText}</div>}

      {current && (
        <WeightPanel
          category={current}
          onScored={setProducts}
          onReset={() => api.products(current.id, lang).then(setProducts)}
        />
      )}

      {compareIds.length >= 2 && (
        <CompareTable ids={compareIds} criteria={current?.criteria ?? []} />
      )}

      <main className="layout">
        <section className="list-column">
          <ListToolbar
            products={products}
            shown={visible.length}
            filter={filter}
            onChange={setFilter}
          />
          {products.length > 0 && visible.length === 0 ? (
            <p className="panel empty">{t.app.noMatch}</p>
          ) : (
            <ProductList
              products={visible}
              selected={selected}
              compareIds={compareIds}
              onSelect={setSelected}
              onToggleCompare={toggleCompare}
            />
          )}
        </section>
        {selected ? (
          <ProductDetailPanel id={selected} criteria={current?.criteria ?? []} />
        ) : (
          <aside className="panel empty">
            <p>{t.app.pickProduct}</p>
            <button className="link" onClick={() => setGuideTab("reading")}>
              {t.app.howToRead}
            </button>
          </aside>
        )}
      </main>

      <GuideDrawer
        open={guideTab !== null}
        tab={guideTab ?? "start"}
        category={current}
        onTab={setGuideTab}
        onClose={closeGuide}
      />
    </div>
  );
}
