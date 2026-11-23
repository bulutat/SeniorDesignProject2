import { useEffect, useState } from "react";
import { api } from "../api";
import { useI18n } from "../i18n";
import type { Criterion, ProductDetail } from "../types";

export default function ProductDetailPanel({ id, criteria }: { id: string; criteria: Criterion[] }) {
  const { lang, t, formatTl, formatNum } = useI18n();
  const [p, setP] = useState<ProductDetail | null>(null);

  // Refetched on a language change: the explanation sentences come from the API in that language.
  useEffect(() => {
    let current = true;
    api.product(id, lang).then((d) => current && setP(d));
    return () => {
      current = false;
    };
  }, [id, lang]);

  if (!p || p.id !== id) return <aside className="panel">{t.app.loading}</aside>;

  return (
    <aside className="panel">
      <div className="detail-head">
        <span className={`score big ${p.label}`}>{Math.round(p.score)}</span>
        <div>
          <h2>{p.name}</h2>
          <span className={`chip ${p.label}`}>{t.labels[p.label]}</span>
        </div>
      </div>

      <dl className="facts">
        <div><dt>{t.detail.price}</dt><dd>{formatTl(p.price_tl)}</dd></div>
        <div><dt>{t.detail.tco(p.lifetime_years)}</dt><dd>{formatTl(p.tco_tl)}</dd></div>
        <div><dt>{t.detail.annual}</dt><dd>{formatNum(p.annual_kwh)} kWh</dd></div>
        <div><dt>{t.detail.energyClass}</dt><dd>{p.energy_class ?? "—"}</dd></div>
      </dl>

      <h3>{t.detail.why}</h3>
      <ul className="explanations">
        {p.explanations.map((e) => (
          <li key={e.criterion} className={e.direction}>
            <span className="impact">{e.impact > 0 ? "+" : ""}{formatNum(e.impact, 1)}</span>
            {e.text}
          </li>
        ))}
      </ul>

      <h3>{t.detail.criteria}</h3>
      <ul className="bars">
        {criteria.map((c) => (
          <li key={c.id}>
            <span>{c.name}{p.imputed.includes(c.id) && <em className="muted"> {t.detail.noData}</em>}</span>
            <span className="bar"><span style={{ width: `${p.sub_scores[c.id] ?? 0}%` }} /></span>
            <span className="num">{formatNum(p.sub_scores[c.id])}</span>
          </li>
        ))}
      </ul>

      <p className="muted small">{t.detail.footer(p.review_stats.n_reviews, p.method)}</p>
    </aside>
  );
}
