# API sözleşmesi (v0)

Kodda karşılığı: `src/greenchoice/schemas.py` (Python) ve `frontend/src/types.ts` (TypeScript).
API çalışırken etkileşimli dokümantasyon: http://localhost:8000/docs

| Metot | Yol | Açıklama | Yanıt |
|---|---|---|---|
| GET | `/api/health` | Servis ve veritabanı durumu | `{status, db_exists}` |
| GET | `/api/categories` | Kategoriler, kriterler, varsayılan ağırlıklar | `Category[]` |
| GET | `/api/products` | Ürün listesi | `ProductSummary[]` |
| GET | `/api/products/{id}` | Ürün detayı, alt skorlar, açıklamalar | `ProductDetail` |
| GET | `/api/products/{id}/explain` | Yalnızca açıklamalar | `Explanation[]` |
| GET | `/api/compare?ids=a,b,c` | 2–4 ürünün detayı | `ProductDetail[]` |
| POST | `/api/score` | Kullanıcı ağırlıklarıyla yeniden skorlama | `ProductSummary[]` |

`/api/products` sorgu parametreleri: `category`, `q` (ad/marka araması), `label`,
`sort` (`score` | `price` | `tco`), `limit` (1–500).

`/api/score` gövdesi:

```json
{ "category": "refrigerator",
  "weights": { "energy_efficiency": 0.5, "price_advantage": 0.1 } }
```

Verilmeyen kriterler varsayılan ağırlığını korur; ağırlıklar toplamı 1 olacak şekilde ölçeklenir.

Örnek `ProductDetail` (kısaltılmış):

```json
{
  "id": "s-rf-01", "name": "Kuzey NF480 No-Frost Buzdolabı 480 L", "category": "refrigerator",
  "price_tl": 38999, "energy_class": "C", "score": 78.4,
  "label": "recommended", "label_text": "Önerilir",
  "annual_kwh": 182, "tco_tl": 45551, "lifetime_years": 12,
  "sub_scores": { "energy_efficiency": 91.0, "lifetime_cost": 88.2, "durability": 85.7, "...": 0 },
  "imputed": [],
  "explanations": [
    { "criterion": "energy_efficiency", "criterion_name": "Enerji verimliliği",
      "direction": "positive", "impact": 7.9,
      "text": "Enerji verimliliği benzer ürünlerden iyi (enerji sınıfı C, yılda ~182 kWh)." }
  ],
  "review_stats": { "n_reviews": 4, "rating_avg": 4.6, "rating_count": 812,
                    "aspects": { "durability": { "pos": 3, "neg": 0 } } },
  "method": "weighted_v0"
}
```

(Örnekteki sayılar temsilidir.)
