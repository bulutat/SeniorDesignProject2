import { useEffect, useState } from "react";
import { api } from "../api";
import type { Criterion, ProductDetail } from "../types";
import { formatNum, formatTl } from "../format";

export default function ProductDetailPanel({ id, criteria }: { id: string; criteria: Criterion[] }) {
  const [p, setP] = useState<ProductDetail | null>(null);

  useEffect(() => {
    setP(null);
    api.product(id).then(setP);
  }, [id]);

  if (!p) return <aside className="panel">Yükleniyor…</aside>;

  return (
    <aside className="panel">
      <div className="detail-head">
        <span className={`score big ${p.label}`}>{Math.round(p.score)}</span>
        <div>
          <h2>{p.name}</h2>
          <span className={`chip ${p.label}`}>{p.label_text}</span>
        </div>
      </div>

      <dl className="facts">
        <div><dt>Fiyat</dt><dd>{formatTl(p.price_tl)}</dd></div>
        <div><dt>{p.lifetime_years} yıllık toplam maliyet</dt><dd>{formatTl(p.tco_tl)}</dd></div>
        <div><dt>Yıllık tüketim</dt><dd>{formatNum(p.annual_kwh)} kWh</dd></div>
        <div><dt>Enerji sınıfı</dt><dd>{p.energy_class ?? "—"}</dd></div>
      </dl>

      <h3>Neden bu skor?</h3>
      <ul className="explanations">
        {p.explanations.map((e) => (
          <li key={e.criterion} className={e.direction}>
            <span className="impact">{e.impact > 0 ? "+" : ""}{formatNum(e.impact, 1)}</span>
            {e.text}
          </li>
        ))}
      </ul>

      <h3>Kriter puanları</h3>
      <ul className="bars">
        {criteria.map((c) => (
          <li key={c.id}>
            <span>{c.name}{p.imputed.includes(c.id) && <em className="muted"> (veri yok)</em>}</span>
            <span className="bar"><span style={{ width: `${p.sub_scores[c.id] ?? 0}%` }} /></span>
            <span className="num">{formatNum(p.sub_scores[c.id])}</span>
          </li>
        ))}
      </ul>

      <p className="muted small">
        {p.review_stats.n_reviews} yorum analiz edildi · Yöntem: {p.method}
      </p>
    </aside>
  );
}
