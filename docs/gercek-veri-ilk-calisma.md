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
yalnızca 10/40'ı. Ortalama skor: çamaşır makinesi 82,0, buzdolabı 67,0. Kriterlerin ortalama skor
katkısı (ağırlık × kriter, puan):

| Kriter | Buzdolabı | Çamaşır makinesi | Fark |
|---|---|---|---|
| Servis | 9,9 (ağırlık 0,10) | 19,7 (ağırlık 0,20) | **9,8** |
| Dayanıklılık | 16,3 (0,20) | 19,9 (0,25) | 3,6 |
| Enerji verimliliği | 10,7 (0,25) | 13,0 (0,15) | 2,3 |
| Uzun vadeli maliyet | 14,2 (0,25) | 13,8 (0,20) | -0,4 |
| Fiyat avantajı | 6,8 (0,10) | 6,6 (0,10) | -0,2 |
| Memnuniyet | 9,1 (0,10) | 9,0 (0,10) | -0,1 |
| Toplam | 67,0 | 82,0 | 15,0 |

Farkın büyük kısmı servisten geliyor: servis kriteri neredeyse her üründe 0,98–0,99 (madde 2), ama
çamaşır makinesinde iki kat ağırlıklı. Yani çamaşır makineleri ürünleri ayırt etmeyen bir kriterden
yaklaşık 10 puan fazla alıyor ve 70 eşiğini kolayca geçiyor.

Enerji sınıfı da farklı dağılıyor (buzdolaplarında A yok, çoğu E), ama etkisi küçük:

| Enerji sınıfı | A | C | D | E | F | Yok |
|---|---|---|---|---|---|---|
| Buzdolabı | 0 | 1 | 4 | 14 | 1 | 20 |
| Çamaşır makinesi | 26 | 2 | 0 | 0 | 0 | 12 |

> Düzeltme: Bu raporun ilk sürümünde (aynı gün) farkın nedeni enerji sınıfının mutlak ölçeği olarak
> yazılmıştı. Enerji kategori içinde göreli puanlanınca sonuç neredeyse değişmedi (aşağıda), katkı
> hesabı asıl nedenin servis ağırlığı olduğunu gösterdi.

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
toplam maliyet kriterleri kategori medyanıyla dolduruluyor; açıklamada gösterilmiyor. Verisi eksik
ürünler ortalamada **daha yüksek** skor alıyor: çamaşır makinesinde 85,0'a karşı 80,5, buzdolabında
67,7'ye karşı 66,2. Medyan, verisi olan zayıf ürünlerden iyi olduğu için eksik veri ödüllendiriliyor.
Garanti süresi hiçbir üründe yok.

**4. Hiç "Önerilmez" yok.** Eşikler (70 ve 45) mutlak. En düşük skor 50,5.

## Seçeneklerin denenmesi

Skorlama kodu değiştirilmeden, aynı kriter değerleriyle yeniden hesaplandı (07.11.2026).

| Seçenek | Buzdolabı (Önerilir / Nötr / Önerilmez) | Çamaşır makinesi |
|---|---|---|
| Şimdiki: mutlak enerji, eşik 70/45 | 10 / 30 / 0 | 37 / 3 / 0 |
| Enerji kategori içinde göreli, eşik 70/45 | 10 / 30 / 0 | 36 / 4 / 0 |
| Kategori içi sıralama: üst %30 Önerilir, alt %20 Önerilmez | 12 / 20 / 8 | 12 / 20 / 8 |

- Enerjiyi göreli yapmak sıralamayı neredeyse değiştirmiyor (kategori içi Spearman 0,994 ve 0,999,
  ilk 10 ürün aynı). Bu yüzden tek başına çözüm değil.
- Kriterlerin ürünler arasındaki etkisi (katkının standart sapması, puan): servis ve memnuniyet
  0,3–0,4; enerji 1,9–2,5; fiyat 2,0–2,2; dayanıklılık 1,8–3,6; uzun vadeli maliyet 3,5–4,2.
  Sıralamayı fiilen maliyet, dayanıklılık, fiyat ve enerji belirliyor.

## Karar gerektirenler (Kişi B ile, B3 skorlama)

- **Etiket:** Mutlak 70/45 eşikleri yerine kategori içi sıralama (yukarıdaki üçüncü satır) ya da
  eşiklerin ürün etiketleriyle (ground truth) ayarlanması. Sıralama her kategoride dengeli etiket
  verir ama "kategorinin en kötüsü bile iyi olabilir" durumunu yok sayar.
- **Servis ağırlığı:** Servis kriteri şu an ayırt etmediği için 0,20 ağırlık yalnızca kategoriler
  arası farkı büyütüyor. Ağırlık azaltılabilir ya da servis kriteri BERTurk sonuçlarından sonra
  yeniden değerlendirilebilir.
- **Eksik enerji verisi:** Medyan yerine kategorinin alt çeyreği (temkinli varsayım) ya da "veri yok"
  olarak ayrı gösterme; açıklamada belirtme. Şu an eksik veri ürüne avantaj sağlıyor.
- **Enerji ölçeği:** Mutlak ölçek kalabilir; sürdürülebilirlik açısından anlamlı ve sıralamayı
  bozmuyor. Arayüzde "AB ölçeğinde E" bilgisi açıkça gösterilmeli.

Bu kararlar verilmeden skorlama kodu değiştirilmedi.
