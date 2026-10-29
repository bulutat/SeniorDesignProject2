# Pilot ürün listesi (B0.2 · Kişi B)

Teslim: **31.10.2026**, kategori başına 10 ürün, Kişi A'ya. A'nın yorum scraper'ı bu
listeyle başlar. Tam liste (80–100 ürün/kategori) 05.11'de.

## Dosya

`data/templates/pilot_products.csv` dosyasını `data/raw/pilot_products.csv` olarak kopyala
ve her ürün için bir satır doldur. Kolonlar `products.csv` sözleşmesiyle aynıdır
(`docs/data-contracts.md`), böylece aynı satırlar sonra gerçek ürün tablosuna girer.

| Kolon | Zorunlu | Ne yazılır |
|---|---|---|
| `product_id` | evet | Kaynak öneki + sitedeki ürün numarası, ör. `ty-123456` (küçük harfli önek, tire, harf/rakam) |
| `source` | evet | `trendyol` veya `hepsiburada` |
| `url` | evet | Ürün sayfası, `https://` ile başlamalı |
| `category` | evet | `refrigerator` veya `washing_machine` |
| `model_code` | evet | Sitedeki model kodu (EPREL eşleştirmesi bununla yapılır) |
| `name` | evet | Ürün adı |
| `brand`, `price_tl`, `energy_class`, `capacity`, `noise_db`, `warranty_years`, `rating_avg`, `rating_count` | hayır | Sayfada **gördüğün** değer. Görmediğini boş bırak |

Fiyat `12.499,90 TL` gibi yazılabilir. Sitede `A++` gibi eski ölçek sınıfı yazıyorsa aynen
yaz: sınıf boş sayılır, ham değer saklanır. Enerji kWh ve su değerlerini buradan değil
EPREL'den alıyoruz.

Ürün seçerken: en az 30 yorumu olanlar, farklı marka ve fiyat aralıkları.

## Kontrol

```bash
greenchoice check-pilot --products data/raw/pilot_products.csv --eprel data/raw/eprel_manual.csv --out data/interim/pilot_products.csv
```

- Hatalı satır varsa satır numarasıyla durur (eksik zorunlu alan, tekrar eden `product_id`
  veya `url`, bilinmeyen kategori, bozuk `product_id`).
- Rapor: kategori başına ürün sayısı, hedefin (10) altında kalan kategoriler,
  `eprel_matched` ve EPREL kaydı henüz olmayan model kodları (`eprel_missing`).
- `--out` ile yazılan `product_id, url, category` dosyası Kişi A'ya verilir. `data/interim/`
  repoya girmez, dosyayı doğrudan paylaş.
