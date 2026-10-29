# Veri toplama Excel dosyası (Kişi B)

İki CSV'yi (pilot ürün listesi ve EPREL değerleri) elle doldurmak zor olduğu için tek bir
Excel dosyası kullanılır. Türkçe Excel, virgülle ayrılmış CSV'yi tek sütun gösterebilir;
`.xlsx` bu sorunu yaşamaz.

**Dosya:** `data/raw/veri_toplama.xlsx` (boş şablon: `data/templates/veri_toplama.xlsx`).
`data/raw/` repoya girmez.

## Sayfalar

| Sayfa | Ne için |
|---|---|
| Nasıl doldurulur | Kısa talimat |
| Ürünler | Trendyol/Hepsiburada ürünleri, her ürün için bir satır |
| EPREL | Aynı ürünlerin EPREL sayfasındaki değerler, her ürün için bir satır |

Her sayfada 1. satır başlık, 2. satır ipucu, **veriler 3. satırdan başlar**. Turuncu
başlıklı (`*`) alanlar zorunlu, gri olanlar isteğe bağlı. Site, kategori ve enerji sınıfı
açılır listeden seçilir.

İki sayfa `Model kodu` ile eşleşir: EPREL sayfasına yazdığın model kodu Ürünler sayfasındaki
ile aynı olmalı (boşluk ve tire farkı sorun olmaz).

## Kurallar

- Zorunlu alanı eksik ürünü yazma, başka ürüne geç. Model kodu yoksa EPREL'le eşleşemez.
- EPREL'de bulamadığın ürün için EPREL sayfasına satır ekleme, Ürünler'de kalsın.
  Eşleşme oranını raporda kullanacağız.
- Sayfada **gördüğün** değeri yaz, görmediğini boş bırak. Sayıları sayı olarak yaz
  (`182,5`), yanına TL veya kWh yazma.
- Ortada boş satır bırakma.
- Çamaşır makinesinde enerji, su ve gürültünün EPREL sayfasında hangi etiketle yazdığını
  `Not` kolonuna aynen yaz.

## CSV'ye çevirme ve kontrol

```bash
greenchoice import-sheets --xlsx data/raw/veri_toplama.xlsx --out-dir data/raw
greenchoice check-pilot --products data/raw/pilot_products.csv --eprel data/raw/eprel_manual.csv --out data/interim/pilot_products.csv
```

`import-sheets`, `data/raw/pilot_products.csv` ve `data/raw/eprel_manual.csv` dosyalarını
yazar ve hemen kontrol eder. Hata varsa hangi satırda olduğunu söyler: **Excel'deki satır,
mesajdaki satır numarasının 1 fazlasıdır** (ortada boş satır varsa kayar).

Şablonu yeniden üretmek için: `greenchoice make-sheets --out data/raw/veri_toplama.xlsx`
(mevcut dosyanın üzerine yazar, doldurulmuş dosyada kullanma).
