import { useEffect, useState } from "react";
import { api } from "../api";
import { useI18n } from "../i18n";
import type { Criterion, ProductDetail } from "../types";

export default function CompareTable({ ids, criteria }: { ids: string[]; criteria: Criterion[] }) {
  const { lang, t, formatTl, formatNum } = useI18n();
  const [items, setItems] = useState<ProductDetail[]>([]);

  useEffect(() => {
    api.compare(ids, lang).then(setItems);
  }, [ids, lang]);

  if (!items.length) return null;

  return (
    <section className="compare">
      <h2>{t.compare.title}</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th />
              {items.map((p) => <th key={p.id}>{p.name}</th>)}
            </tr>
          </thead>
          <tbody>
            <tr><th>{t.compare.score}</th>{items.map((p) => <td key={p.id}><strong>{Math.round(p.score)}</strong> · {t.labels[p.label]}</td>)}</tr>
            <tr><th>{t.compare.price}</th>{items.map((p) => <td key={p.id}>{formatTl(p.price_tl)}</td>)}</tr>
            <tr><th>{t.compare.tco}</th>{items.map((p) => <td key={p.id}>{formatTl(p.tco_tl)}</td>)}</tr>
            <tr><th>{t.compare.kwh}</th>{items.map((p) => <td key={p.id}>{formatNum(p.annual_kwh)}</td>)}</tr>
            {criteria.map((c) => (
              <tr key={c.id}>
                <th>{c.name}</th>
                {items.map((p) => <td key={p.id}>{formatNum(p.sub_scores[c.id])}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
