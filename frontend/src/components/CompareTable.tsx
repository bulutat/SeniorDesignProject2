import { useEffect, useState, type ReactNode } from "react";
import { api } from "../api";
import { bestIndexes, energyRank, type Better } from "../compareBest";
import { useI18n } from "../i18n";
import type { Criterion, ProductDetail } from "../types";
import EnergyBadge from "./EnergyBadge";

interface Row {
  key: string;
  head: string;
  value: (p: ProductDetail) => number | null | undefined; // for finding the best cell
  better: Better;
  show: (p: ProductDetail) => ReactNode;
}

export default function CompareTable({ ids, criteria }: { ids: string[]; criteria: Criterion[] }) {
  const { lang, t, formatTl, formatNum } = useI18n();
  const [items, setItems] = useState<ProductDetail[]>([]);

  useEffect(() => {
    api.compare(ids, lang).then(setItems);
  }, [ids, lang]);

  if (!items.length) return null;

  const rows: Row[] = [
    { key: "score", head: t.compare.score, value: (p) => p.score, better: "higher",
      show: (p) => <><strong>{Math.round(p.score)}</strong> · {t.labels[p.label]}</> },
    { key: "price", head: t.compare.price, value: (p) => p.price_tl, better: "lower",
      show: (p) => formatTl(p.price_tl) },
    { key: "tco", head: t.compare.tco, value: (p) => p.tco_tl, better: "lower",
      show: (p) => formatTl(p.tco_tl) },
    { key: "kwh", head: t.compare.kwh, value: (p) => p.annual_kwh, better: "lower",
      show: (p) => formatNum(p.annual_kwh) },
    { key: "energy", head: t.compare.energyClass, value: (p) => energyRank(p.energy_class),
      better: "lower", show: (p) => <EnergyBadge value={p.energy_class} /> },
    // Values filled with the category median are not the product's own data: they never win.
    ...criteria.map((c): Row => ({
      key: c.id, head: c.name, better: "higher",
      value: (p) => (p.imputed.includes(c.id) ? null : p.sub_scores[c.id]),
      show: (p) => <>{formatNum(p.sub_scores[c.id])}{p.imputed.includes(c.id) && <em className="muted small"> {t.detail.noData}</em>}</>,
    })),
  ];

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
            {rows.map((r) => {
              const best = bestIndexes(items.map(r.value), r.better);
              return (
                <tr key={r.key}>
                  <th>{r.head}</th>
                  {items.map((p, i) => (
                    <td key={p.id} className={best.has(i) ? "best" : undefined}>
                      {r.show(p)}
                      {best.has(i) && <span className="visually-hidden"> ({t.compare.best})</span>}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="compare-legend muted small"><span className="best-dot" aria-hidden="true" /> {t.compare.legend}</p>
    </section>
  );
}
