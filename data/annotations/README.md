# Manuel etiketler

Bu klasör repoya girer: etiketler projenin altın verisidir.

| Dosya | Biçim | Kim / ne zaman |
|---|---|---|
| `reviews_gold.csv` | `review_id, product_id, annotator, text, aspect, polarity` | İki kişi, Aşama 1 sonu – 20.11 |
| `product_labels.csv` | `product_id, annotator, label, note` | İki kişi bağımsız, Aşama 3 ilk haftası |

- Yorum dosyasında bir yorum birden çok aspect içeriyorsa her aspect ayrı satırdır.
  Hiç aspect içermeyen yorum, `aspect` ve `polarity` boş bırakılarak tek satırla yazılır.
- `annotator` değerleri: `A` veya `B`. Ortak etiketlenen 100 yorum ve tüm ürünler
  iki kişi tarafından ayrı ayrı etiketlenir, uyum Cohen's kappa ile ölçülür.
- `label` değerleri: `recommended`, `neutral`, `not_recommended`.
- Kurallar: `docs/annotation-guideline.md`.
