# Durum raporu ve Kişi A için yapılacaklar

Tarih: 30.10.2026 · Hazırlayan: Kişi B · Yapay zekâ kuralları: [AGENTS.md](../AGENTS.md)

Bu dosya iki kişi içindir: Kişi A (NLP ve açıklanabilirlik) ne yapılmış, sırada ne var diye
buradan başlasın. Yapay zekâ asistanına görev verirken de önce bu dosyayı ve `AGENTS.md`'yi
okutun. Kişi A'nın şu ana kadar yaptıklarını bilmiyorum; aşağıdaki "başlamadı" ifadeleri
"B tarafında bir kayıt görmüyorum" anlamındadır, güncelleyin.

> Bu rapordaki çalışmalar `atahan/eprel-erisim` dalında. Pull Request birleşene kadar `main`'de
> yoktur: dalı çekin (`git fetch; git switch atahan/eprel-erisim`).

## 1. Şu ana kadar yapılanlar

**İskelet (22.10):** pipeline, SQLite şeması, FastAPI (7 uç nokta), React arayüzü, kural tabanlı
aspect çıkarımı, ağırlıklı skor (`weighted_v0`), açıklama şablonları. Sentetik örnek veriyle
uçtan uca çalışır.

**Bu dalda eklenenler (Kişi B):**

| Konu | Ne oldu |
|---|---|
| Ortam | Python 3.12, Node, Git kuruldu; `pytest` **72 test geçiyor**, `ruff` temiz, arayüz derleniyor |
| EPREL | Public API anahtarı **imzalı beyan** istiyor, bu yüzden değerler EPREL sayfalarından **elle** toplanıyor. Etiket adları ve arama davranışı `docs/kaynak-inceleme.md`'de |
| Veri toplama | Tek Excel dosyası (`greenchoice make-sheets`, `import-sheets`), katı doğrulayıcılar, `check-pilot` raporu |
| Pilot liste | **26 ürün:** 12 buzdolabı, 14 çamaşır makinesi. 5'i Trendyol, 21'i Hepsiburada. EPREL eşleşmesi 26/26, ama ürünleri EPREL'de bulunanlar arasından seçtik (seçim yanlılığı) |
| Hata düzeltmeleri | Boş yorum tablosuyla pipeline çökmesi giderildi (yorumlar gelmeden de çalışır) |
| Varsayımlar | Su fiyatı İSKİ 2026 (65,52 TL/m³), çamaşır makinesi ömrü 12 yıl, yılda 220 yıkama doğrulandı. **Elektrik fiyatı doğrulanamadı** (açık) |
| Dokümanlar | `decisions.md` karar 10–14, `kaynak-inceleme.md`, toplantı gündemi `meetings/2026-10-31.md` |

**Henüz yok:** gerçek yorum verisi, ürün/yorum scraper'ı, BERTurk, TF-IDF, AHP, ML modelleri,
SHAP, kullanıcı çalışması, etiketlenmiş veri (`reviews_gold.csv` ve `product_labels.csv` boş).

## 2. Sana verilen girdi

**`data/interim/pilot_products.csv`** (Kişi B elden verir, Git'e girmez). Kolonlar:
`product_id, url, category`.

- 26 ürün. Önek `ty-` Trendyol, `hb-` Hepsiburada. `category`: `refrigerator` veya
  `washing_machine`.
- **İki site var.** Koddaki tek stub `TrendyolSource`. Hepsiburada için kaynak sınıfı
  gerekecek ya da ortak yapı çıkarılacak.
- **Hepsiburada `product_id`'lerini adreslerden aldım**, ürünün gerçek numarası olduğunu
  doğrulamadım. Eşleştirmede güvenilir kimlik olarak `url`'yi kullan.
- **Yorum sayısı düşük ürünler var.** 9 Siemens çamaşır makinesinin 7'sinde 30'dan az yorum
  görünüyor (biri 1, biri 4), biri tam 30, yalnızca biri 60. Bunlardan anlamlı veri çıkmayabilir, hangilerinin tutulacağına
  birlikte karar verin.
- Tam liste (kategori başına 80–100 ürün) 05.11'de gelecek.

## 3. Yapman gerekenler (sırayla)

1. **Ortamı kur ve doğrula.** `README.md` kurulum bölümü. `pytest` 72 test geçmeli.
2. **Oku:** `docs/gorev-dagilimi.md`, `docs/data-contracts.md`, `docs/annotation-guideline.md`,
   `docs/decisions.md`, `docs/kaynak-inceleme.md`, `AGENTS.md`.
3. **A0.1 · Yorum kaynağını incele (plan: 22–28.10).** Tarayıcı Geliştirici Araçları → Network
   sekmesinde yorum isteğini bul (genelde JSON). Sayfalama, ürün başına yorum sayısı,
   `robots.txt` ve kullanım şartlarını kontrol et. Çıktı: `docs/kaynak-inceleme.md` içinde
   "Yorumlar" bölümü ve hangi sitenin seçileceği önerisi. Bitti sayılır: bir ürünün ilk 50
   yorumu çekilebiliyor.
4. **A0.2 · NLP ön araştırması (24–31.10).** Türkçe ABSA ve BERTurk için 5–8 kaynak,
   Colab'da BERTurk'ün çalıştığını gör. Çıktı: `docs/literatur.md` NLP bölümü.
5. **A1.1 · Yorum scraper'ı (27.10–05.11).** `fetch_reviews` yazılır (`collect/ecommerce.py`,
   arayüz: `collect/base.py`). `PoliteClient` kullanılır (en az 2 sn bekleme, önbellek).
   Ürün başına en fazla 300 yorum. Kesilirse kaldığı yerden devam etmeli. Çıktı:
   `data/raw/` ve `data/interim/reviews.csv` (sütunlar `contracts.REVIEW_COLUMNS`:
   `review_id, product_id, rating, text, date`; `review_id` kaynak önekli ve benzersiz,
   `product_id` pilot listedekiyle aynı). Bitti sayılır: iki kategoride en az 60'ar ürünün
   yorumu toplanmış.
   - Testlerde **canlı ağ kullanma**: gerçek yanıttan küçük bir örnek kaydet, onunla test et.
   - Seçici ve JSON alan adlarını gerçek yanıtı görmeden yazma (`AGENTS.md`, kural 1).
6. **A1.2 · Yorum temizleme (03–08.11).** Uzatılmış harfler ("çoooook"), emoji, yalnızca
   kargo/satıcı yorumları, Türkçe dışı yorumlar. Her kural için bir test (`preprocess/reviews.py`).
7. **A1.3 · Etiketleme kılavuzu (01–07.11).** `docs/annotation-guideline.md` taslağını 30 gerçek
   yorumla dene, belirsizlikleri örnek olarak ekle, B onaylar.
8. Sonrası: etiketleme (10–20.11, ortak), train/val/test bölünmesi (12.11), BERTurk
   fine-tune (18.11–02.12), yöntem karşılaştırması (28.11–05.12). Ayrıntı: `gorev-dagilimi.md`.

## 4. Teslim noktaları

| Tarih | Kim → kime | Ne |
|---|---|---|
| 31.10 | B → A | Pilot ürün listesi (**verildi**) · danışman toplantısı (`meetings/2026-10-31.md`) |
| 05.11 | B → A | Tam ürün listesi (80–100 ürün/kategori) |
| 10.11 | A + B | Veri sözleşmesi v1, `data/interim/` dolu, `greenchoice build --source interim` çalışıyor |
| 12.11 | A → B | Etiketli yorumlar için train/val/test bölünmesi (sabit seed) |
| 05.12 | A → B | BERTurk çıktısı `review_aspects` tablosunda (`method = berturk_v0`) |

## 5. Dikkat edilecekler

- `main`'e doğrudan commit yok: dal → PR → diğer kişinin onayı.
- `data/raw`, `data/interim`, `data/processed`, `models/` Git'e girmez, dosyayı elden paylaşın.
- Sözleşme kolonlarını (`contracts.py`) silmek/yeniden adlandırmak iki kişinin onayını ister.
- `greenchoice build --source interim` yorum dosyası boş olsa da çalışır; yorumsuz ürünlerin
  yorum tabanlı kriterleri medyanla doldurulur ve açıklamada kullanılmaz.
- Çözülmemiş sorular: elektrik fiyatı, buzdolabı ömrü kaynağı, hangi site(ler), eşleşme oranı
  için seçim yanlılığı. Hepsi `decisions.md` ve toplantı gündeminde.

## 6. Yapay zekâya görev verirken

Şu kalıp işe yarar:

```text
AGENTS.md ve docs/devir-kisi-a.md dosyalarını oku. Görev: <A1.1 gibi tek bir görev>.
Kurallara uy: uydurma yok, önce test, küçük adım, README güncelle. Önce planı yaz,
doğrulayamadığın her şeyi açıkça "doğrulanmadı" diye işaretle.
```

Bir seferde tek milestone isteyin (özellik + test + doğrulama + README). Asistanın yazdığı her
parser ve her sayı gerçek yanıtla karşılaştırılmadan kabul edilmemeli.
