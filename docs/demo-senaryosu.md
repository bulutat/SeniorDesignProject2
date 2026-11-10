# Demo senaryosu (ara sunum, 13.11.2026)

Süre: **2,5 dakika** (sunum 8 dakika; 2–3 dakika demo). Konuşma İngilizce, arayüz Türkçe.
Sayılar 10.11.2026'daki `demo/entegrasyon` veritabanından (80 ürün, kural tabanlı NLP, varsayılan
ağırlıklar). Veritabanı yeniden kurulursa sayılar değişebilir: provadan önce kontrol edin.

**Okumayın.** Aşağıdaki İngilizce cümleler ne söyleneceğinin özeti; ezberlemeyin, kendi cümlelerinizle
anlatın. Hoca sunumda bir yerden okumanın notu düşürdüğünü söylüyor.

## Akış

### 1. Açılış: ne görüyoruz? (20 sn)

- Ekran: ana sayfa, **Çamaşır makinesi** sekmesi.
- Söylenecek: "This is GreenChoice running on real data: 80 products from Hepsiburada and Trendyol,
  energy data from EPREL and official manufacturer labels, and about 3,400 customer reviews. Each
  product gets a score from 0 to 100 and a label."

### 2. En iyi ürün neden en iyi? (45 sn)

- Tıkla: listenin başındaki **Grundig GNWM 81612 A** (skor 90, Önerilir, 20.005 TL, A sınıfı).
- Göster, sırayla:
  1. **Kriter çubukları:** toplam maliyet 94,7; fiyat 94,6; enerji 93,5.
  2. **12 yıllık toplam maliyet:** ~31.411 TL (fiyat + 12 yıllık elektrik ve su).
  3. **Açıklamalar:** "12 yıllık toplam kullanım maliyeti benzer ürünlerden düşük", "fiyatı avantajlı",
     "yorumlarda dayanıklılık olumlu (2 olumlu, 0 olumsuz)".
- Söylenecek: "The score is not a black box. Each sentence comes from the criterion that moved the
  score most, and review-based claims show how many reviews support them."

### 3. A sınıfı tek başına yetmez (45 sn)

- **Karşılaştır** kutusunu işaretle: Grundig ve **Bosch WGA242Z0TR** (listenin sonlarında, skor 61,6, Nötr).
- Karşılaştırma tablosunda göster (tablo skoru tam sayıya yuvarlar; enerji sınıfı tabloda yok, listede
  iki üründe de "Enerji sınıfı A" yazıyor):

  | | Grundig GNWM 81612 A | Bosch WGA242Z0TR |
  |---|---|---|
  | GreenChoice skoru | 90 · Önerilir | 62 · Nötr |
  | Fiyat | 20.005 TL | 69.749 TL |
  | Toplam maliyet | ~31.411 TL | ~82.174 TL |
  | Yıllık kWh | ~103 | ~108 |

- Söylenecek: "Both are class A and use almost the same energy, but over twelve years the Bosch costs
  about fifty thousand lira more. An energy label alone would rate them the same; GreenChoice shows the
  difference."

### 4. Kullanıcı kendi önceliğini seçer (35 sn)

- Aç: **"Sizin için hangi kriter ne kadar önemli?"**
- Seç: Enerji verimliliği → **Çok önemli**, Fiyat avantajı → **Önemli değil**. **Yeniden sırala**.
- Göster: liste değişir; Samsung WW90CGC04DAEAH birinci olur, Grundig ikinci.
- Söylenecek: "Even if price does not matter to me, the expensive Bosch only moves from 39th to 37th,
  because the twelve-year cost still includes what you pay at the till."
- **Varsayılana dön**.

### 5. Kapanış (5 sn)

- Söylenecek: "Next, we replace the keyword rules with a fine-tuned BERTurk model trained on our
  labelled reviews."

## Gelebilecek sorular ve kısa cevaplar

- **Buzdolaplarında neden A sınıfı yok?** Listedeki 39 buzdolabının sınıfı biliniyor: 28 E, 6 F, 4 D, 1 C.
  Verimli modeller pahalı ve az değerlendirilmiş; seçim kuralımız (en az 30 değerlendirme) onları dışarıda
  bıraktı. Bunu bir sınır olarak raporluyoruz.
- **Yorumlardan ne çıkarıyorsunuz?** Beş aspect: dayanıklılık, enerji, servis, arıza, gürültü; her biri
  olumlu/olumsuz. Şu an kural tabanlı; 400 yorumu elle etiketleyip BERTurk ve TF-IDF ile karşılaştıracağız.
- **Neden enerji yorumlardan alınmıyor?** 1.460 pilot yorumda enerjiden söz eden çok az yorum vardı;
  enerji resmî etiketten (sınıf ve yıllık kWh) geliyor (karar 16).
- **Ağırlıklar nereden?** Şimdilik taslak; AHP ile gerekçelendireceğiz (araç hazır).
- **Veriyi nasıl topladınız?** Siteler otomatik toplamaya izin vermediği için sayfalar tarayıcıdan elle
  kaydedildi ve çevrimdışı okundu; enerji verisi EPREL ve üretici etiketlerinden.
- **Yeşil skor = ucuz mu?** Hayır, ama bu veride verimli ürünün yüksek fiyatı 12 yılda nadiren geri ödeniyor
  (duyarlılık analizi); bu yüzden enerji kriterinin değeri çevresel tarafta.

## Demodan önce (prova günü ve sunum günü)

1. `demo/entegrasyon` dalında olun, veritabanını kurun:
   ```bash
   greenchoice import-reviews
   ```
   ```bash
   greenchoice build --source interim --eprel data/raw/v4/eprel_manual.csv
   ```
2. API ve arayüzü başlatın (iki ayrı terminal; API veritabanını açılışta okur, yeniden kurulumdan sonra
   API'yi yeniden başlatın):
   ```bash
   .venv/Scripts/uvicorn greenchoice.api.main:app --port 8000
   ```
   ```bash
   cd frontend && npm run dev
   ```
3. Tarayıcıda http://localhost:5173, yakınlaştırma %110–125 (projeksiyonda okunsun).
4. Yukarıdaki sayıları bir kez kontrol edin (Grundig 90, Bosch 61,6; tabloda 62).
5. **Yedek:** Demo bozulursa diye dört adımın ekran görüntüsünü veya kısa bir ekran kaydını slayta koyun.
6. İnternet gerekmez; her şey yerel.

## Bilinen tuzaklar

- **Arçelik 9100 DMX** enerji ağırlığı artınca üçüncü sıraya çıkıyor, ama sınıfı yalnızca mağaza
  başlığından geliyor (kWh yok). Demoda bu ürünü öne çıkarmayın.
- Buzdolabı listesinde 8. sıradaki Bosch KGN56VWD0N'nin hiç metinli yorumu yok (yorum kriterleri medyanla
  dolduruluyor). Buzdolabı göstermeyecekseniz sorun değil.
- Karşılaştırma tablosunda enerji sınıfı satırı yok; sınıfı listeden veya detay panelinden gösterin.
