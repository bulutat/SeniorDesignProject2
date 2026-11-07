# Manuel etiketler

Bu klasör repoya girer: etiketler projenin altın verisidir. **Yorum metni bu klasöre yazılmaz**;
metin `data/interim/reviews.csv` içinde kalır ve `review_id` ile eşleştirilir.

| Dosya | Biçim | Kim / ne zaman |
|---|---|---|
| `reviews_gold.csv` | `review_id, product_id, split, aspect, polarity` | `greenchoice collect-labels` üretir |
| `reviews_labels_raw.csv` | `review_id, annotator, aspect, polarity` | Aynı komut; her kişinin kendi etiketleri (kappa için) |
| `kappa.csv` | `aspect, reviews, agreement, kappa, labelled_A, labelled_B` | Aynı komut; ortak test yorumlarında |
| `product_labels.csv` | `product_id, annotator, label, note` | İki kişi bağımsız, Aşama 3 ilk haftası |

- Bir yorum birden çok aspect içeriyorsa her aspect ayrı satırdır. Hiç aspect içermeyen yorum,
  `aspect` ve `polarity` boş bırakılarak tek satırla yazılır.
- `split`: `test` (ortak 100 yorum, yalnızca sonuç raporu), `train`, `val` (train'in %20'si,
  eşik ayarı için). Bölünme `nlp/pool.py` ve `nlp/labels.py` içinde sabit tohumla yapılır.
- Test yorumlarında iki kişinin farklı etiketlediği hücreler `data/interim/etiketleme/uzlasma.csv`
  dosyasına yazılır; karar verilmeyen yorumlar altın etikete girmez.
- `annotator` değerleri: `A` veya `B`. `label` değerleri: `recommended`, `neutral`, `not_recommended`.
- Kurallar: `docs/annotation-guideline.md`.
