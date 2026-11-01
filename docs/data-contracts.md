# Veri sözleşmeleri (v0)

Kodda karşılığı: `src/greenchoice/contracts.py`. Kolon **eklemek** serbesttir. Kolon
**kaldırmak veya yeniden adlandırmak** diğer kişinin kodunu bozar; ikinizin onayıyla
yapılır ve bu dosya güncellenir. 10.11.2026 kontrol noktasında v1'e çevrilecek.

## products

Aşama 1 çıktısı. Ham hali `data/interim/products.csv`, temiz hali SQLite `products` tablosu.

| Kolon | Tip | Açıklama |
|---|---|---|
| `product_id` | str | Kaynak önekli benzersiz id (`ty-123456`) |
| `source` | str | `trendyol`, `hepsiburada`, `sample` … |
| `url` | str | Ürün sayfası |
| `category` | str | `refrigerator` veya `washing_machine` |
| `brand`, `model_code`, `name` | str | `model_code` EPREL eşleştirmesinde kullanılır |
| `price_tl` | float | Temizlemede `"12.499,90 TL"` → `12499.9` |
| `energy_class` | str | A–G (2021 ölçeği). Eski ölçek (A+++) boş bırakılır |
| `energy_class_raw` | str | Sitedeki ham değer (temizlemede eklenir) |
| `energy_kwh_per_year` | float | Buzdolabı |
| `energy_kwh_per_100_cycles` | float | Çamaşır makinesi |
| `water_l_per_cycle` | float | Çamaşır makinesi |
| `capacity` | float | Litre / kg |
| `noise_db`, `warranty_years` | float | |
| `rating_avg`, `rating_count` | float | Sitedeki puan özeti |
| `annual_kwh`, `tco_tl` | float | Türetilmiş (`preprocess/tco.py`) |
| `eprel_matched` | bool | EPREL eşleşmesi bulundu mu |

## reviews

| Kolon | Tip | Açıklama |
|---|---|---|
| `review_id` | str | Kaynak önekli benzersiz id |
| `product_id` | str | `products.product_id` |
| `rating` | float | 1–5 |
| `text` | str | Ham metin |
| `text_clean` | str | Normalize metin (temizlemede eklenir) |
| `text_product` | str | `text_clean` + teslimat bağlamındaki "sorunsuz/sağlam" sözcükleri çıkarılmış hali. Aspect çıkarımı bunu kullanır |
| `mentions_logistics` | bool | Yorumda kargo, satıcı veya teslimat geçiyor mu. Filtre değil, bilgi amaçlı |
| `truncated` | bool | Metin "Devamını Oku" açılmadan kaydedilmiş (`import-reviews`) |
| `site_aspects` | str | Hepsiburada kriter puanları, JSON (`import-reviews`) |
| `date` | str | ISO tarih |

## review_aspects

NLP çıktısı. Yorum başına 0..n satır; aynı yorumda aynı (aspect, polarity) bir kez yer alır.

| Kolon | Değerler |
|---|---|
| `review_id` | |
| `aspect` | `durability`, `energy`, `service`, `failure`, `noise` (`config/aspects.yaml`) |
| `polarity` | `pos`, `neg` |
| `method` | `rule_based_v0`, `tfidf_v0`, `berturk_v0` … |
| `evidence` | Eşleşen ifade (kural tabanlı) veya boş |

## product_features

`products` + yorum toplulaştırması + kriter alt skorları. Skorlamanın girdisi.

| Kolon grubu | Açıklama |
|---|---|
| `products` kolonları | yukarıdaki gibi |
| `n_reviews`, `review_rating_avg` | Temizlenmiş yorum sayısı ve ortalama puanı |
| `<aspect>_pos`, `<aspect>_neg` | Aspect'i olumlu/olumsuz anan yorum sayısı |
| `<aspect>_score` | `(pos − neg) / (pos + neg + 2)`, [-1, 1] |
| `service_issue_rate` | Servis veya arıza şikâyeti içeren yorum oranı |
| `c_<kriter>` | 0–1 alt skor (6 kriter) |
| `imputed` | Medyanla doldurulan kriterler, virgülle ayrılmış |

## scores

| Kolon | Açıklama |
|---|---|
| `product_id`, `category` | |
| `method` | `weighted_v0`, `xgboost_v0` … |
| `score` | 0–100 |
| `label` | `recommended`, `neutral`, `not_recommended` |
| `sub_scores_json` | `{"energy_efficiency": 82.5, …}` (0–100) |
| `explanations_json` | `[{"criterion", "criterion_name", "direction", "impact", "text"}, …]` |
