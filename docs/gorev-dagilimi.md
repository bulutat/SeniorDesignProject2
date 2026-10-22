# Görev dağılımı (rev. 2 · 22.10.2026)

İskelet kurulduktan sonra güncellenen dağılım. Takvimin görsel hali: [takvim.html](takvim.html).

## Roller

| | Kişi A · NLP ve açıklanabilirlik | Kişi B · Veri, skorlama ve web |
|---|---|---|
| **Ana sorumluluk** | Yorumların toplanması ve analizi, BERTurk, SHAP ile açıklamalar, kullanıcı çalışması | Ürün ve enerji verisi, kriter ve skor hesabı, ML model karşılaştırması, API ve arayüz |
| **Sahibi olduğu kod** | `collect/` (yorum kısmı), `preprocess/reviews.py`, `nlp/transformer.py`, `explain/` | `collect/` (ürün, EPREL), `preprocess/products.py, matching.py, tco.py`, `nlp/tfidf.py`, `nlp/rule_based.py`, `scoring/`, `api/`, `frontend/` |
| **ML bileşeni (raporda savunacağı)** | BERTurk ile aspect tabanlı duygu analizi | LR / RF / XGBoost ile skor modeli, AHP ağırlıkları |
| **Rapor bölümleri** | NLP yöntemi ve sonuçları, açıklanabilirlik, kullanıcı çalışması | Veri seti, skorlama yöntemi, ML karşılaştırması, sistem mimarisi ve arayüz |

"Sahibi olmak", o kodun çalışmasından ve testlerinden sorumlu olmak demek. Diğer kişi de
değişiklik yapabilir ama PR'ı sahibi onaylar.

## İskeletle biten işler

Bunlar artık takvimde yok; yerlerine aşağıdaki iyileştirme görevleri geldi.

- Repo, klasör yapısı, ortam, CI
- TCO hesabı, SQLite şeması, veri sözleşmeleri
- Yorum temizlemenin temel hali (normalizasyon, spam, kopya, kısa yorum)
- Kural tabanlı aspect çıkarımı, ürün düzeyinde toplulaştırma, P/R/F1 değerlendirme script'i
- Ağırlıklı baseline skor, 0–100 normalizasyon, kriter alt skorları
- Açıklama şablonları (ağırlıklı model için)
- FastAPI (7 endpoint), React iskeleti (liste, detay, karşılaştırma, ağırlık slider'ı)

## Teslim noktaları (A ↔ B)

Paralel çalışmanın birbirini beklediği yerler. Tarihe uymak, diğer kişinin işini bloke etmemek demek.

| Tarih | Kim → kime | Ne teslim edilir |
|---|---|---|
| 31.10 | B → A | Pilot ürün listesi: kategori başına 10 ürün (`product_id`, `url`). A'nın yorum scraper'ı bununla başlar |
| 05.11 | B → A | Tam ürün listesi (kategori başına 80–100 ürün) |
| 10.11 | A + B | Veri sözleşmesi v1 (`docs/data-contracts.md`), `data/interim/` dolu, `greenchoice build --source interim` çalışıyor |
| 12.11 | A → B | Etiketli yorumların train/val/test bölünmesi (sabit seed). Üç NLP yöntemi **aynı test setiyle** ölçülür |
| 05.12 | A → B | BERTurk çıktısı `review_aspects` tablosunda (`method = berturk_v0`). B'nin ML modelleri bu özellikleri kullanır |
| 12.12 | A + B | Uzlaşılmış ürün etiketleri (`data/annotations/product_labels.csv`) |
| 20.12 | B → A | Eğitilmiş en iyi ML modeli ve özellik matrisi. A bununla SHAP açıklamalarını üretir |
| 10.01 | A → B | `/explain` için SHAP tabanlı açıklama formatı. B arayüze bağlar |

---

## Aşama 0 · Kararlar ve keşif (22.10 – 31.10)

### A0.1 · Yorum kaynağını inceleme · 22.10 – 28.10 · Kişi A
- **Ne:** Trendyol ve Hepsiburada'da yorumların nasıl yüklendiğini bulmak. Tarayıcının
  Geliştirici Araçları → Network sekmesinde yorum isteği (genelde JSON) aranır. Sayfalama,
  ürün başına yorum sayısı, robots.txt ve kullanım koşulları kontrol edilir.
- **Çıktı:** `docs/kaynak-inceleme.md` → "Yorumlar" bölümü ve hangi sitenin seçileceğine dair öneri.
- **Bitti sayılır:** Bir ürünün ilk 50 yorumu elle (veya küçük bir script'le) çekilebiliyor.

### A0.2 · NLP ön araştırması · 24.10 – 31.10 · Kişi A
- **Ne:** Türkçe aspect-based sentiment analysis ve BERTurk fine-tune üzerine 5–8 kaynak okumak.
  Colab'da BERTurk'ün yüklenip birkaç cümle üzerinde çalıştığını görmek.
- **Çıktı:** `docs/literatur.md` → NLP bölümü (kaynak + 2–3 cümle özet).

### B0.1 · EPREL erişim testi · 22.10 – 28.10 · Kişi B
- **Ne:** EPREL'e API ile mi toplu indirmeyle mi erişileceğini bulmak, API anahtarı gerekiyorsa
  başvurmak. Buzdolabı ve çamaşır makinesinden 5'er model kodunu elle sorgulayıp alan adlarını
  doğrulamak.
- **Çıktı:** `collect/eprel.py` içindeki `FIELD_MAP` ve URL'ler doğrulanmış; `docs/kaynak-inceleme.md` → "EPREL" bölümü.

### B0.2 · Ürün sayfasını inceleme · 26.10 – 30.10 · Kişi B
- **Ne:** Kategori listeleme sayfası nasıl sayfalanıyor; ürün sayfasında fiyat, model kodu,
  enerji sınıfı ve teknik özellikler nerede. 20 ürünün model kodunu EPREL'de elle aramak.
- **Çıktı:** Tahmini EPREL eşleşme oranı (ör. "20'de 16"). Oran düşükse yedek planı konuşmak.
- **Teslim:** 31.10'a kadar pilot ürün listesi (kategori başına 10 ürün) → Kişi A.

### B0.3 · Varsayımların kaynakları · 26.10 – 31.10 · Kişi B
- **Ne:** Güncel elektrik ve su birim fiyatları (EPDK / belediye tarifeleri), ürün ömrü
  varsayımları (buzdolabı 12, çamaşır makinesi 10 yıl) için kaynak bulmak.
- **Çıktı:** `config/categories.yaml` güncel değerlerle, kaynaklar `docs/decisions.md`'de.

### O0.1 · Danışman toplantısı · 31.10 · Ortak
- **Gündem:** kategori ve site seçimi, ground truth yöntemi, az verili ürünler, rol dağılımı.
- **Çıktı:** `docs/meetings/2026-10-31.md`, kararlar `docs/decisions.md`'ye işlenmiş.

### O0.2 · Ortamın iki bilgisayarda çalışması · 22.10 – 27.10 · Ortak (ağırlıkla Ali Rubar)
- **Ne:** Repo klonlanır, README'deki kurulum yapılır, `pytest` ve arayüz çalıştırılır.
- **Bitti sayılır:** İki bilgisayarda da 26 test geçiyor ve arayüz açılıyor.

---

## Aşama 1 · Veri toplama ve ön işleme (27.10 – 10.11)

### A1.1 · Yorum scraper'ı · 27.10 – 05.11 · Kişi A
- **Ne:** `TrendyolSource.fetch_reviews` (veya seçilen site) yazılır. `PoliteClient` kullanılır:
  istekler arası en az 2 sn, önbellek açık. Ürün başına en fazla 300 yorum.
- **Girdi:** B'nin ürün listesi (önce 10'luk pilot, 05.11'de tam liste).
- **Çıktı:** `data/raw/` altında ham yorumlar, `data/interim/reviews.csv` (REVIEW_COLUMNS).
- **Bitti sayılır:** İki kategoride en az 60'ar ürünün yorumları toplanmış; script yarıda
  kesilirse kaldığı yerden devam ediyor.

### A1.2 · Yorum temizlemenin genişletilmesi · 03.11 – 08.11 · Kişi A
- **Ne:** Gerçek veriye bakarak eksikleri tamamlamak: uzatılmış harfler ("çoooook"),
  emoji, yalnızca kargo/satıcıdan bahseden yorumlar, Türkçe dışı yorumlar.
- **Çıktı:** `preprocess/reviews.py` güncel, her yeni kural için bir test.

### A1.3 · Etiketleme kılavuzunun kesinleşmesi · 01.11 – 07.11 · Kişi A
- **Ne:** `docs/annotation-guideline.md` taslağını 30 gerçek yorumla denemek, belirsiz
  durumları örnek olarak eklemek. B'nin onayıyla kesinleşir.

### B1.1 · Ürün scraper'ı · 27.10 – 04.11 · Kişi B
- **Ne:** `iter_product_urls` ve `fetch_product` yazılır. Kategori başına 80–100 ürün,
  önceliği en az 30 yorumu olanlara verir.
- **Çıktı:** `data/interim/products.csv` (PRODUCT_COLUMNS). 05.11'de tam liste → Kişi A.

### B1.2 · EPREL eşleştirmesi · 01.11 – 08.11 · Kişi B
- **Ne:** İlgili ürün gruplarının EPREL verisi çekilir, `merge_eprel` ile eşleştirilir.
  Eşleşmeyen model kodları için elle düzeltme tablosu tutulur.
- **Çıktı:** `data/raw/eprel_*.csv`, `data/annotations/model_code_fixes.csv`, eşleşme oranı raporu.
- **Bitti sayılır:** Ürünlerin en az %70'inde enerji verisi EPREL'den geliyor.

### B1.3 · Gerçek veriyle uçtan uca çalışma · 06.11 – 10.11 · Kişi B
- **Ne:** `greenchoice build --source interim --eprel ...` gerçek veriyle çalıştırılır,
  çıkan hatalar düzeltilir, arayüzde gerçek ürünler görünür.

### B1.4 · Keşifsel veri analizi (EDA) · 04.11 – 10.11 · Kişi B
- **Ne:** Fiyat, kWh, enerji sınıfı ve yorum sayısı dağılımları; eksik veri oranları;
  aspect anılma sıklıkları (kural tabanlı çıkarımla).
- **Çıktı:** `notebooks/01_B_eda.ipynb`; rapordaki "Veri seti" bölümü için 3–4 grafik.

### O1.1 · Etiketleme altyapısı · 07.11 – 10.11 · Ortak
- **Ne:** Label Studio kurulur (veya paylaşılan bir tablo kullanılır), 400 yorumluk etiketleme
  havuzu seçilir: iki kategoriden ve farklı puanlardan dengeli.
- **Kontrol noktası 10.11:** veri sözleşmesi v1 ve `data/interim/` dolu.

---

## Aşama 2 · NLP ve özellik çıkarımı (10.11 – 05.12)

### O2.1 · Yorum etiketleme · 10.11 – 20.11 · Ortak
- **Ne:** Her kişi ~300 yorum etiketler; bunların 100'ü ortaktır. Ortak 100 üzerinden
  aspect bazında Cohen's kappa hesaplanır (A hesaplar). Kappa < 0,6 olan aspect'ler konuşulur.
- **Çıktı:** `data/annotations/reviews_gold.csv`, kappa tablosu.
- **Teslim 12.11 (A):** train / val / test bölünmesi.

### A2.1 · BERTurk fine-tune · 18.11 – 02.12 · Kişi A
- **Ne:** `nlp/transformer.py` yazılır. Çok etiketli sınıflandırma (`aspect:polarity`),
  `dbmdz/bert-base-turkish-cased`. Eğitim Google Colab GPU'da, model `models/` altına.
  Etiketleme bitmeden ilk 200 etiketle deneme eğitimine başlanabilir.
- **Bitti sayılır:** Test setinde P/R/F1 ölçülmüş, `TransformerExtractor` pipeline'da seçilebiliyor.

### A2.2 · Hata analizi ve yöntem karşılaştırması · 28.11 – 05.12 · Kişi A
- **Ne:** Üç yöntem (kural, TF-IDF, BERTurk) aynı test setinde karşılaştırılır. Yanlış
  sınıflanan 30–50 örnek kategorilere ayrılır (olumsuzlama, ironi, yazım hatası …).
- **Çıktı:** Karşılaştırma tablosu ve hata analizi (rapor bölümü taslağı).
- **Teslim 05.12 → B:** BERTurk çıktısı `review_aspects` tablosunda.

### B2.1 · TF-IDF + LR/SVM baseline · 12.11 – 24.11 · Kişi B
- **Ne:** `nlp/tfidf.py`: `AspectExtractor` arayüzünü uygulayan TF-IDF + Logistic Regression
  (ve/veya Linear SVM). A'nın test bölünmesiyle değerlendirilir.
- **Çıktı:** P/R/F1 sonuçları A'nın karşılaştırma tablosuna girer.

### B2.2 · Kural sözlüğünün gerçek veriyle genişletilmesi · 18.11 – 26.11 · Kişi B
- **Ne:** Etiketli verideki kaçırılan ifadelerle `config/aspects.yaml` genişletilir
  (yalnızca **train** setine bakılarak, test setine bakılmaz).

### B2.3 · Skorlamanın iyileştirilmesi · 24.11 – 05.12 · Kişi B
- **Ne:**
  1. Kapasiteye göre enerji normalizasyonu (ör. litre / kg başına kWh).
  2. Az verili ürün işareti: yorum sayısı eşik altındaysa veya kriterlerin önemli kısmı
     doldurulmuşsa `low_confidence` olarak işaretlenir, "Önerilir" etiketi verilmez.
  3. Min-max yerine yüzdelik sıralamanın denenmesi (aykırı değerler için).
- **Çıktı:** `scoring/criteria.py` güncel, testler, `docs/decisions.md`'ye karar notu.

### O2.2 · Literatür taraması · 15.11 – 05.12 · Ortak
- **A:** NLP / ABSA / Türkçe NLP. **B:** çok kriterli karar verme (AHP), sürdürülebilir tüketim,
  enerji etiketleri.
- **Çıktı:** `docs/literatur.md` ve raporun "İlgili çalışmalar" bölümü taslağı.

---

## Aşama 3 · Skorlama modeli (05.12 – 31.12)

### O3.1 · Ürün etiketleme (ground truth) · 05.12 – 12.12 · Ortak
- **Ne:** 150–200 ürün, iki kişi birbirinden bağımsız ve sistem skorunu görmeden
  Önerilir / Nötr / Önerilmez olarak etiketler. Kappa hesaplanır, uyuşmazlıklar konuşulup
  uzlaşılmış etiket belirlenir.
- **Çıktı:** `data/annotations/product_labels.csv`.

### B3.1 · AHP ile kriter ağırlıkları · 05.12 – 14.12 · Kişi B
- **Ne:** Her kategori için kriterlerin ikili karşılaştırma matrisi (ikiniz ve isterseniz
  danışman doldurur), ağırlıklar ve tutarlılık oranı (CR < 0,1).
- **Çıktı:** `scoring/ahp.py`, `config/categories.yaml` ağırlıkları güncel (`weighted_v1`).

### B3.2 · ML model karşılaştırması · 12.12 – 24.12 · Kişi B
- **Ne:** `scoring/ml.py` ile LR, Random Forest ve XGBoost; stratified k-fold CV.
  Girdi: kriter alt skorları + ham özellikler (BERTurk aspect özellikleri dahil).
  Hedef: uzlaşılmış ürün etiketleri. `weighted_v0`, `weighted_v1` ve ML modelleri aynı
  ölçütlerle karşılaştırılır: accuracy, macro F1, Spearman.
- **Çıktı:** Karşılaştırma tablosu; en iyi model pipeline'da seçilebilir (`--scorer`).
- **Teslim 20.12 → A:** eğitilmiş model ve özellik matrisi.

### B3.3 · Duyarlılık analizi · 20.12 – 31.12 · Kişi B
- **Ne:** Elektrik fiyatı ±%50 ve ağırlıklar değiştiğinde sıralama ne kadar değişiyor
  (Kendall tau). "Ucuz ama verimsiz ürün ne zaman pahalıya gelir?" sorusunu cevaplar.
- **Çıktı:** Raporun "Tartışma" bölümü için 1–2 grafik.

### A3.1 · SHAP ile açıklamalar · 15.12 – 31.12 · Kişi A
- **Ne:** ML modelleri için katkılar SHAP değerlerinden hesaplanır, `explain/` modülüne
  aynı formatta (`contributions`) verilir. B'nin modeli gelmeden önce örnek veride bir
  Random Forest ile başlanır.
- **Bitti sayılır:** ML modelinin skorladığı her ürün için Türkçe açıklama üretiliyor.

### A3.2 · Açıklamalara yorum kanıtı eklemek · 20.12 – 31.12 · Kişi A
- **Ne:** "Yorumlarda dayanıklılık olumlu" gibi cümlelere, BERTurk'ün bulduğu yorumlardan
  kısa bir örnek alıntı eklemek ("…3 yıldır sorunsuz…").
- **Çıktı:** `explain/` güncel, API'de `evidence` alanı.

### B3.4 · Arayüzün gerçek veriye geçişi · 18.12 – 31.12 · Kişi B
- **Ne:** Arama, filtre (enerji sınıfı, fiyat aralığı), sıralama (skor / fiyat / TCO),
  az verili ürün uyarısı.

---

## Aşama 4 · Açıklanabilirlik, arayüz ve teslim (01.01 – 25.01)

### A4.1 · Kullanıcı çalışması tasarımı · 01.01 – 10.01 · Kişi A
- **Ne:** 10–15 katılımcı için görevli anket. Önerilen tasarım: katılımcı iki ürün
  arasında seçim yapar, bir kez açıklamasız bir kez açıklamalı. Anlaşılabilirlik ve güven
  Likert ölçeğiyle ölçülür.
- **Çıktı:** Anket formu, görev senaryoları, `docs/kullanici-calismasi.md`.

### A4.2 · Açıklamaların API'ye bağlanması · 05.01 – 12.01 · Kişi A
- **Ne:** `/api/products/{id}/explain` seçilen skorlayıcıya göre (ağırlıklı / ML) açıklama döner.
- **Teslim 10.01 → B:** son açıklama formatı.

### A4.3 · Kullanıcı çalışması analizi · 18.01 – 22.01 · Kişi A
- **Ne:** Sonuçların analizi (ortalama, açıklamalı / açıklamasız karşılaştırma), grafikler.

### B4.1 · Arayüzün son hali · 01.01 – 15.01 · Kişi B
- **Ne:** Görsel tasarım, karşılaştırma ekranında grafik, skor kırılımı, mobil uyum,
  açıklamaların ve yorum kanıtlarının gösterimi.

### B4.2 · Deploy ve demo · 13.01 – 20.01 · Kişi B
- **Ne:** Uygulama Render veya Hugging Face Spaces'e yüklenir, demo için ürün seti sabitlenir.
- **Bitti sayılır:** Danışmanın açabileceği bir bağlantı var.

### O4.1 · Kullanıcı testi · 14.01 – 19.01 · Ortak
- Her kişi 7–8 katılımcıyla testi yürütür.

### O4.2 · Final rapor · 05.01 – 25.01 · Ortak
- Bölüm sahipleri yukarıdaki "Roller" tablosunda. Her kişi diğerinin bölümlerini okuyup yorumlar.

### O4.3 · Sunum ve demo videosu · 20.01 – 25.01 · Ortak
- **Kontrol noktası 25.01:** proje teslimi.

---

## Haftalık rutin

- **Pazartesi:** 15 dk senkron: geçen hafta ne bitti, bu hafta ne yapılacak, ne bloke ediyor.
- **Danışman toplantısı:** notlar `docs/meetings/` altına.
- **Her görev:** ayrı dal → PR → diğer kişinin onayı → `main`.
