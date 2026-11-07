# Gerçek veriyle ilk uçtan uca çalışma (B1.3)

07.11.2026, Kişi A (Kişi B'nin görevi, B yoğun olduğu için). Skorlama kodu değiştirilmedi;
aşağıdakiler mevcut `weighted_v0` yönteminin gerçek veriyle verdiği sonuçlardır.

## Nasıl çalıştırıldı

```bash
greenchoice import-sheets --xlsx data/raw/v4/veri_toplama_v4.xlsx --out-dir data/raw/v4
cp data/raw/v4/pilot_products.csv data/interim/products.csv
greenchoice import-reviews
greenchoice build --source interim --eprel data/raw/v4/eprel_manual.csv
```

`veri_toplama_v4.xlsx` Kişi B'nin dosyasının kopyasıdır (yalnızca okundu). Bütün girdi ve çıktı
dosyaları `data/raw`, `data/interim`, `data/processed` altında kalır, repoya girmez.

## Sonuç

| | Değer |
|---|---|
| Ürün | 80 (40 buzdolabı, 40 çamaşır makinesi) |
| EPREL eşleşmesi | 48 / 80 |
| Temizlik sonrası yorum | 3.386 (ham 3.467) |
| Kural tabanlı aspect eşleşmesi | 1.135 |
| Etiket | 47 Önerilir, 33 Nötr, **0 Önerilmez** |

API (`/api/categories`, `/api/products`) gerçek ürünleri döndürüyor.

## Bulgular

**1. Etiket büyük ölçüde kategoriye bağlı.** Çamaşır makinelerinin 37/40'ı "Önerilir", buzdolaplarının
yalnızca 10/40'ı. Ortalama skor: çamaşır makinesi 81,9, buzdolabı 67,0. Nedeni enerji sınıfı:

| Enerji sınıfı | A | C | D | E | F | Yok |
|---|---|---|---|---|---|---|
| Buzdolabı | 0 | 1 | 4 | 14 | 1 | 20 |
| Çamaşır makinesi | 26 | 2 | 0 | 0 | 0 | 12 |

Enerji sınıfı mutlak ölçekte puanlanıyor (A = 1, G = 0). Buzdolaplarında A sınıfı hiç yok, çoğu E.
Enerji verimliliği kriterinin ortalaması buzdolabında 0,43, çamaşır makinesinde 0,87.
Sürdürülebilirlik açısından bu doğru olabilir (E sınıfı gerçekten daha az verimli), ama kullanıcı
tek bir kategori içinde seçim yaptığı için etiket ürünleri ayırt etmiyor: neredeyse bütün çamaşır
makineleri "Önerilir".

**2. Yorum kriterleri neredeyse sabit.** Kategori ortalaması ve standart sapması:

| Kriter | Buzdolabı | Çamaşır makinesi |
|---|---|---|
| Servis | 0,99 ± 0,03 | 0,98 ± 0,02 |
| Memnuniyet | 0,91 ± 0,03 | 0,90 ± 0,04 |
| Dayanıklılık | 0,81 ± 0,09 | 0,79 ± 0,14 |
| Fiyat avantajı | 0,68 ± 0,22 | 0,66 ± 0,20 |
| Uzun vadeli maliyet | 0,57 ± 0,17 | 0,69 ± 0,18 |
| Enerji verimliliği | 0,43 ± 0,10 | 0,87 ± 0,13 |

Servis ve memnuniyet ürünleri ayırt etmiyor: yorumların %87'si 5 yıldız ve kural tabanlı yöntem
servis sorununu çok az buluyor. Skoru fiilen fiyat, toplam maliyet ve enerji belirliyor.

**3. Eksik enerji verisi.** 32 üründe enerji sınıfı yok (buzdolabında 20). Bu ürünlerde enerji ve
toplam maliyet kriterleri kategori medyanıyla dolduruluyor; açıklamada gösterilmiyor ama skorda
ürünü ortalamaya çekiyor. Garanti süresi hiçbir üründe yok.

**4. Hiç "Önerilmez" yok.** Eşikler (70 ve 45) mutlak. En düşük skor 50,5.

## Karar gerektirenler (Kişi B ile, B3 skorlama)

- **Enerji sınıfı ölçeği:** Mutlak mı kalsın, kategori içinde göreli mi olsun, yoksa ikisi
  ayrı gösterilsin mi (ör. "kategorisinin en verimlisi" + "AB ölçeğinde E")?
- **Etiket eşikleri:** Mutlak 70/45 yerine kategori içi sıralama (ör. üst %30 Önerilir, alt %20
  Önerilmez) ya da eşiklerin ürün etiketleriyle (ground truth) ayarlanması.
- **Az bilgi veren kriterler:** Servis ve memnuniyetin ağırlığı ya da hesaplanışı. BERTurk servis
  sorunlarını daha iyi bulursa servis kriteri değişebilir; karar NLP sonuçlarından sonra verilebilir.
- **Eksik enerji verisi:** Medyanla doldurmak yerine "veri yok" diye ayrı göstermek ya da
  bu ürünleri enerji kriterinde cezalandırmamak; açıklamada belirtmek.

Bu kararlar verilmeden skorlama kodu değiştirilmedi.
