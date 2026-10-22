import { useEffect, useState } from "react";
import { api } from "../api";
import type { Criterion, ProductDetail } from "../types";
import { formatNum, formatTl } from "../format";

export default function CompareTable({ ids, criteria }: { ids: string[]; criteria: Criterion[] }) {
  const [items, setItems] = useState<ProductDetail[]>([]);

  useEffect(() => {
    api.compare(ids).then(setItems);
  }, [ids]);

  if (!items.length) return null;

  return (
    <section className="compare">
      <h2>Karşılaştırma</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th />
              {items.map((p) => <th key={p.id}>{p.name}</th>)}
            </tr>
          </thead>
          <tbody>
            <tr><th>GreenChoice skoru</th>{items.map((p) => <td key={p.id}><strong>{Math.round(p.score)}</strong> · {p.label_text}</td>)}</tr>
            <tr><th>Fiyat</th>{items.map((p) => <td key={p.id}>{formatTl(p.price_tl)}</td>)}</tr>
            <tr><th>Toplam maliyet</th>{items.map((p) => <td key={p.id}>{formatTl(p.tco_tl)}</td>)}</tr>
            <tr><th>Yıllık kWh</th>{items.map((p) => <td key={p.id}>{formatNum(p.annual_kwh)}</td>)}</tr>
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
