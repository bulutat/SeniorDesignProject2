# Duyarlılık analizi (B3.3)

07.11.2026, Kişi A (Kişi B'nin görevi). Komut: `greenchoice sensitivity` (`scoring/sensitivity.py`).
Girdi: gerçek veriyle üretilen veritabanı (80 ürün, `weighted_v0`, kural tabanlı NLP; bkz.
`gercek-veri-ilk-calisma.md`). Her senaryoda yalnızca bir varsayım değişir; TCO, kriterler ve skor
aynı ürün verisinden yeniden hesaplanır ve kategori içindeki sıralama temel durumla karşılaştırılır.

## Sıralama ne kadar değişiyor?

Kendall tau (1 = sıralama aynı), ilk 10 ürünün örtüşmesi ve etiketi değişen ürün sayısı (40 üründen):

| Senaryo | Buzdolabı tau | Çamaşır m. tau | İlk 10 (B / Ç) | Etiket değişen (B / Ç) |
|---|---|---|---|---|
| Elektrik -%50 | 0,997 | 0,998 | 10 / 10 | 1 / 0 |
| Elektrik +%50 | 0,983 | 0,997 | 10 / 10 | 1 / 0 |
| Elektrik yüksek kademe (4,321 TL/kWh) | 0,986 | 0,997 | 10 / 10 | 1 / 0 |
| Ömür 8 yıl | 0,998 | 0,997 | 10 / 10 | 1 / 0 |
| Ömür 15 yıl | 0,990 | 0,998 | 10 / 10 | 1 / 0 |
| Dayanıklılık ağırlığı -%50 | 0,891 | 0,894 | 9 / 9 | 5 / 1 |
| Uzun vadeli maliyet ağırlığı -%50 | 0,904 | 0,943 | 9 / 10 | 7 / 2 |
| Fiyat ağırlığı -%50 | 0,905 | 0,936 | 8 / 10 | 3 / 0 |
| Enerji ağırlığı -%50 | 0,944 | 0,982 | 10 / 10 | 13 / 2 |
| Servis ağırlığı ±%50 | 0,988–0,994 | 0,983–0,991 | 10 / 10 | 4–8 / 1–3 |
| Memnuniyet ağırlığı ±%50 | 0,985–0,990 | 0,989–0,990 | 10 / 10 | 3–5 / 0–2 |
| Eşit ağırlıklar | 0,887 | 0,886 | 9 / 7 | 19 / 0 |

Bütün senaryolar: komutun çıktısı (yukarıdaki tablo bir seçkidir; ağırlıkların +%50 hâli de vardır).

**Sonuçlar:**

- **Elektrik fiyatı ve ömür sıralamayı neredeyse hiç değiştirmiyor** (tau ≥ 0,98, ilk 10 aynı). Toplam
  maliyette fiyat farkları, enerji maliyeti farklarından çok büyük (aşağıda).
- **Sıralama en çok ağırlıklara duyarlı**, özellikle dayanıklılık, toplam maliyet ve fiyat. Bunlar
  ürünler arasında en çok değişen kriterler. Ağırlıkların gerekçesi (AHP, B3.1) bu yüzden önemli.
- **Servis ve memnuniyet ağırlığını değiştirmek sıralamayı değiştirmiyor**: iki kriter de ürünler
  arasında neredeyse sabit (`gercek-veri-ilk-calisma.md`, madde 2).
- **Etiketler sıralamadan daha kırılgan**, özellikle buzdolabında: buzdolaplarının çoğu 70 eşiğinin
  hemen altında olduğu için küçük ağırlık değişiklikleri etiketi değiştiriyor (enerji ağırlığı yarıya
  inince 13 ürün). Mutlak eşik yerine kategori içi sıralamayla etiket bu kırılganlığı azaltır.

## Ucuz ama verimsiz ürün ne zaman pahalıya gelir?

Aynı kategoride, ucuz olanın daha çok enerji tükettiği her ürün çifti için iki ürünün ömür boyu
maliyetini eşitleyen elektrik fiyatı (su maliyeti dahil). Yalnızca yıllık kWh bilinen ürünler
(buzdolabında 20, çamaşır makinesinde 28):

| Kategori | Çift | Bugünkü fiyatla (2,919 TL/kWh) verimli olan zaten ucuza geliyor | +%50 fiyatla | Başabaş fiyatın medyanı |
|---|---|---|---|---|
| Buzdolabı | 76 | 1 | 3 | 49,45 TL/kWh |
| Çamaşır makinesi | 104 | 7 | 7 | 103,81 TL/kWh |

- Çiftlerin büyük çoğunluğunda verimli ürünün fiyat farkı, 12 yıllık elektrik tasarrufuyla
  kapanmıyor. Bunun için elektriğin bugünkünün yaklaşık 17 katına (buzdolabı) veya 35 katına
  (çamaşır makinesi) çıkması gerekiyor (medyan).
- Yani bu veride "verimli ürün uzun vadede kendini öder" genel olarak doğru değil; fiyat farkı
  çoğunlukla verimlilikten değil marka, kapasite ve özelliklerden geliyor. Enerji kriterinin değeri
  maliyetten çok çevresel etki tarafında. Raporda bu şekilde yazılmalı.
- Sınırlar: elektrik fiyatı vergiler hariç (karar 14); fiyat artışları ve indirim oranı (para değerinin
  zamanla değişimi) modellenmedi; kWh'ı olmayan 32 ürün dahil değil; kapasite farkı (ör. 9 kg ile
  10 kg) dikkate alınmadı.
