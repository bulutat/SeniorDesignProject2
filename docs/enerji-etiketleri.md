# EPREL dışındaki ürünlerin enerji verisi

10.11.2026, Kişi A. Kod: `src/greenchoice/preprocess/energy_labels.py`. Veri:
`data/manual/energy_labels.csv` (repoya girer; yalnızca kamuya açık etiket bilgisi ve kaynak adresi).

## Neden

80 ürünün 32'sinde enerji sınıfı yoktu (EPREL'de eşleşmeyen veya model kodu olmayan ürünler).
Bu ürünlerde enerji ve toplam maliyet kriterleri kategori medyanıyla dolduruluyordu ve verisi
eksik ürünler ortalamada **daha yüksek** skor alıyordu (`gercek-veri-ilk-calisma.md`, madde 3).
Türkiye pazarına özel modellerin bir kısmı EPREL'de yok veya farklı kodla kayıtlı.

## Kaynak sırası (`energy_source` kolonu)

| Değer | Kaynak | Ürün sayısı |
|---|---|---|
| `eprel` | Kişi B'nin elle topladığı EPREL kaydı | 48 |
| `label` | Üreticinin resmî AB enerji etiketi (PDF), elle okundu | 23 |
| `shop` | Toplanan ürün verisindeki sınıf | 0 (hepsi üstteki kaynaklarla kapsandı) |
| `title` | Mağazadaki ürün adında yazan sınıf ("E Enerji Sınıfı") | 7 |
| (boş) | Bulunamadı | 2 |

Üst kaynak varsa alt kaynak yalnızca boş alanları doldurur; resmî etiketteki sınıf mağaza verisindeki
sınıfın yerine geçer. 2021 öncesi ölçekteki sınıflar (A+++ … D) hiçbir kaynaktan alınmaz, çünkü yeni
A–G ölçeğine çevrilemez.

## Etiketler nasıl okundu

1. Üreticinin Türkiye sitesinde model koduyla arama (Arçelik, Beko, Grundig, Altus, Samsung, Vestel,
   Profilo). Arama sonucundaki kodun ürün adındaki kodla **birebir** aynı olması şartı arandı; renk
   veya kapasite varyantı (ör. RT47CG6636**WW** yerine **S9**) aynı ürün sayılmadı.
2. Ürün sayfasındaki "Enerji Etiketi" PDF'i açıldı, sayfa resme çevrilip sınıf oku ve değerler gözle
   okundu (sınıf oku PDF'te metin değil çizim). Yıllık kWh (buzdolabı) veya 100 yıkamada kWh, yıkama
   başına su ve kapasite (çamaşır makinesi) etiketten alındı.
3. Etiketteki model kimliği dosyada `model_on_label` kolonundadır (ör. "570471 MB 7250820140").
   Arçelik grubu bu kimliği EPREL'de de kullanıyor; ileride EPREL eşleşmesi için işe yarar.

Erişim: siteler normal tarayıcıyla, ürün başına bir arama ve bir ürün sayfası açılarak okundu;
engel veya CAPTCHA ile karşılaşılmadı.

## Belirsizlikler ve eksikler

- **Vestel "Nf 52111" (ty-814492137):** Mağaza adında yalnızca "Nf 52111" yazıyor. Vestel'de NF52111
  (451 L), NF52111 E DuoMode ve NFK52111 ayrı modeller; birebir kod eşleşmesi olan NF52111 alındı.
  Notu dosyada var.
- **Yalnızca ürün adından sınıfı alınan 7 ürün:** LG GN-H702HLHU (E), Samsung RT46K6000S8, RT43K6000WW,
  RT50K6000S8 (F), Hoover HGD 410B9C-17 (A), Arçelik 9100 DMX (A), model kodu olmayan Arçelik 10 kg
  (B). Satıcı metni; kWh yok. LG'nin sitesindeki etiket 2017 tarihli Türkiye etiketi (eski ölçek
  olabilir), bu yüzden kullanılmadı. Eski Samsung modelleri ve Arçelik 9100 DMX üretici sitesinden
  kalkmış.
- **Bulunamayan 2 ürün:** Arçelik 10120 MX (sitede yok; benzer kodlu 10120 MA ayrı model, yerine
  konmadı) ve Samsung RB50RS334WW (Samsung sitesinde etiket yok).
- Etiketler 10.11.2026'da okundu; üretici sayfaları değişebilir, kaynak adresleri dosyadadır.

## Sonuç

Enerji sınıfı 48 → 78 üründe, yıllık kWh 48 → 71 üründe biliniyor. Buzdolaplarında yine A sınıfı
yok (28 E, 6 F, 4 D, 1 C); bu, ürün listesinin özelliği (`docs/` içindeki ürün seçimi notları).
