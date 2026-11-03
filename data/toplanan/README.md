# Toplanan ürün verisi (karar 19)

Bu klasör, toplanan verinin **küçük ve olgusal** kısmını yedeklemek ve ekip arkadaşıyla paylaşmak
içindir: ürün adı, herkese açık ürün adresi, fiyat, puan ve değerlendirme sayısı, EPREL değerleri.
Tarih: 02.11.2026. Fiyatlar ve sayılar günlük değişir, bu dosyalardaki değerler o günün değerleridir.

| Dosya | İçerik | Üreten komut |
|---|---|---|
| `veri_toplama_v4.xlsx` | Güncel 80 ürünlük liste (kategori başına 40) ve ürünlerin EPREL kayıtları. Doldurma kılavuzu: `docs/veri-toplama-excel.md` | `greenchoice make-sheets`, elle doldurma |
| `secilen_urunler.csv` | Karar 18 kuralıyla seçilen 54 ürün | `greenchoice select-candidates` |
| `aday_urunler.csv` | Kaydedilen 15 Hepsiburada arama sayfasındaki 393 aday | `greenchoice import-listings` |
| `trendyol_adaylar.json` | Verilen 17 Trendyol ürün sayfasından okunan ürün bilgisi | `greenchoice fetch-trendyol` |

## Bu klasöre girmeyenler

- Kaydedilen sayfaların kendisi (`data/raw/listeleme_sayfalari`, yaklaşık 214 MB): mağazaların
  telifli sayfaları ve görselleri.
- `data/raw/http_cache`: ham sayfa önbelleği, içinde yorum yazarlarının adları bulunur.
- Yorum metinleri ve `reviews.csv` (`docs/yorum-toplama.md`).
- Anahtar, parola veya kişisel veri.

`tests/test_collected_data.py` bu kuralı denetler: yalnızca `.csv`, `.json`, `.xlsx`, `.md`,
dosya başına en fazla 1 MB ve yazar, yorum metni veya anahtar içeren alan yok.

## Yeniden üretmek

```bash
greenchoice import-listings                      # kaydedilen sayfalar -> aday_urunler.csv
greenchoice select-candidates --listings data/interim/aday_urunler.csv --trendyol data/interim/trendyol_adaylar.json
greenchoice import-sheets --xlsx data/toplanan/veri_toplama_v4.xlsx --out-dir data/raw
```
