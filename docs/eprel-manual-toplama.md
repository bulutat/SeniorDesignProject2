# EPREL değerlerini elle toplama (Kişi B)

EPREL API'si anahtar istediği için (bkz. `kaynak-inceleme.md`), enerji verisi herkese açık
EPREL ürün sayfalarından **elle** okunup bir CSV'ye yazılır. Otomatik toplama yapılmaz.

> Doldurması daha kolay olan yol: [veri-toplama-excel.md](veri-toplama-excel.md). Aşağıdaki
> CSV anlatımı, aynı kolonların ne anlama geldiğini açıklar.

## Başlamadan önce

1. [API şartlar belgesini](https://ec.europa.eu/assets/move-ener/eprel/EPREL%20Public/Public%20API%20Term%20and%20Conditions/API_TERMS_AND_CONDITIONS_EN.pdf)
   oku. Bu belge API içindir ama veri kullanımı hakkında ne dediğini öğrenmek için
   okunmalı. Rapora koyacağın verinin kaynağını göstermen gerekir.
2. `data/templates/eprel_manual.csv` dosyasını `data/raw/eprel_manual.csv` olarak kopyala.
   `data/raw/` repoya girmez.

## Her model için

1. e-ticaret sayfasındaki **model kodunu** al (`products.csv`'deki `model_code`).
2. EPREL'de (`https://eprel.ec.europa.eu`) bu model kodunu ara ve ürün sayfasını aç.
3. Sayfada **gördüğün** değerleri yaz. Görmediğin değeri boş bırak, tahmin etme.
4. `eprel_url` kolonuna ürün sayfasının adresini yapıştır. Adres
   `https://eprel.ec.europa.eu/` ile başlamalı, yoksa dosya reddedilir.

| Kolon | Ne yazılır |
|---|---|
| `model_code` | E-ticaret sitesindeki model kodu (boşluk ve tire farkı sorun olmaz) |
| `product_group` | Adreste geçen grup adı (ör. `refrigeratingappliances2019`). Bilgi amaçlı |
| `energy_class` | **Zorunlu.** `A`–`G` (2021 ölçeği). `A++` gibi eski sınıf kabul edilmez |
| `energy_kwh_per_year` | Buzdolabı. Sayfada "Annual energy consumption (kWh/annum)" |
| `energy_kwh_per_100_cycles` | Çamaşır makinesi |
| `water_l_per_cycle` | Çamaşır makinesi |
| `noise_db` | Gürültü, dB |
| `eprel_url` | **Zorunlu.** Kaynak sayfa |
| `collected_on` | Okuma tarihi, `2026-10-29` biçimi |
| `note` | Sayfada gördüğün etiket adı, belirsizlik, eski/yeni etiket farkı |

Ondalık için virgül ya da nokta kullanılabilir (`182,5` veya `182.5`). Binlik ayracı
kullanma (`1.234,5` reddedilir).

## Çamaşır makinesi etiketleri

Buzdolabı için yalnızca "Annual energy consumption (kWh/annum)" etiketi doğrulandı.
Çamaşır makinesi sayfasında 100 yıkama başına enerji, su ve gürültünün **hangi etiketle**
yazıldığını ilk 5 modelde `note` kolonuna aynen yaz. Eşlemeyi ona göre doğrulayıp bu
tabloya işleyeceğiz.

## Kontrol

```bash
greenchoice build --source interim --eprel data/raw/eprel_manual.csv
```

Hatalı satır varsa komut satır numarasıyla durur. Çıktıdaki `eprel_matched`, enerji verisi
EPREL'den gelen ürün sayısıdır. Hedef: ürünlerin en az %70'i (görev B1.2).
