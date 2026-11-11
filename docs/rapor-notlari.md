# Ara rapor notları (bölüm 2.1, 2.2.5, 2.2.7)

11.11.2026. Ham malzeme: gereksinim listesi, emek ve maliyet tahmini, risk tablosu. Listeler rapora
uygun olsun diye İngilizce; açıklamalar Türkçe. Rapordaki anlatım metnini kendi cümlelerinizle yazın.
Her madde koddaki veya belgelerdeki bir duruma dayanıyor; köşeli parantez içinde nerede olduğu yazıyor.

## 1. Requirements (rapor 2.1)

### Functional requirements

| ID | Requirement | Durum |
|---|---|---|
| FR-1 | The system shall list the products of a selected category (refrigerator, washing machine) with their GreenChoice score (0–100), label, price and energy class. | Var [`/api/products`, ProductList] |
| FR-2 | The system shall show, for a selected product, the sub-score of each of the six criteria, the 12-year total cost of ownership and the annual energy consumption. | Var [`/api/products/{id}`] |
| FR-3 | The system shall explain each score in Turkish sentences derived from the criteria that changed it most; review-based statements shall state how many reviews support them, and criteria filled with an estimate shall not be explained. | Var [`explain/templates.py`] |
| FR-4 | The user shall be able to compare two to four products side by side. | Var [`/api/compare`] |
| FR-5 | The user shall be able to mark each criterion as "not important", "important" or "very important" and re-rank the products accordingly. | Var [WeightPanel, `/api/score`] |
| FR-6 | The user shall be able to search products by name or brand. | Var [`q` parametresi] |
| FR-7 | The system shall import product data from the data collection workbook and energy data from EPREL records and official manufacturer labels, rejecting invalid rows with the file and row number. | Var [`import-sheets`, `energy_labels.py`] |
| FR-8 | The system shall import customer reviews from review pages saved in a browser, without storing user names. | Var [`import-reviews`] |
| FR-9 | The system shall clean reviews: normalise text, remove spam and duplicates, and keep delivery remarks out of the durability signal. | Var [`preprocess/`] |
| FR-10 | The system shall extract aspect-level sentiment (durability, energy, service, failure, noise; positive or negative) from each review, with a selectable method (rule-based, TF-IDF + logistic regression, BERTurk). | Kural tabanlı çalışıyor; diğer ikisi etiket bekliyor |
| FR-11 | The system shall compute the six criteria and a weighted score and label for every product within its category. | Var [`scoring/`] |
| FR-12 | The system shall support review annotation: select a stratified pool, produce one sheet per annotator, validate the sheets, compute Cohen's kappa and build gold labels with train/validation/test splits. | Var [`annotation-pool`, `collect-labels`] |
| FR-13 | The system shall evaluate aspect extraction with precision, recall and F1 on a held-out test set. | Var [`eval-nlp`] |
| FR-14 | The system shall derive criterion weights from pairwise comparisons (AHP) and report the consistency ratio. | Var [`ahp`] |
| FR-15 | The system shall report how the ranking changes when assumptions change (electricity price, lifetime, weights). | Var [`sensitivity`] |
| FR-16 | The system shall compare weighted, AHP-based and machine-learning scorers against manually labelled products. | Planlı (B3.2, ürün etiketleri gerekli) |

### Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Transparency | Every score shall be decomposable into criterion contributions, and the source of each product's energy data (EPREL, label, store data, title) shall be recorded. [`energy_source`] |
| NFR-2 | Legal and ethics | Data shall be collected only in ways the sources allow: no automated collection where `robots.txt` or access controls forbid it, no bypassing of blocks or CAPTCHAs, no user names, and no review text in the code repository. [karar 17] |
| NFR-3 | Performance | The web interface shall answer list and detail requests within one second on a laptop, because all heavy computation is done offline. (Hedef; ölçülmedi.) |
| NFR-4 | Reproducibility | One command shall rebuild the database from the input files; random choices shall use fixed seeds; the test suite shall pass before every merge. [`build`, seed 491, 219 test] |
| NFR-5 | Maintainability | Methods shall sit behind common interfaces (aspect extractor, scorer) so that a new method does not change existing code; each module has one owner and every change is reviewed in a pull request. |
| NFR-6 | Data quality | Invalid input shall stop the pipeline with the file and row named instead of being skipped silently; pre-2021 energy classes shall not be mixed with the A–G scale. |
| NFR-7 | Usability | The interface shall be in Turkish and usable on narrow screens. [CSS 800 px kırılımı] |
| NFR-8 | Portability and cost | The system shall run on a personal computer with free and open-source software; a GPU is needed only for training, using a free cloud notebook. |
| NFR-9 | Privacy (user study) | The user study shall collect no names or contact details; participants are identified only by a code. |

## 2. Zaman, emek ve maliyet tahmini (rapor 2.2.5)

**Yöntem:** Aşağıdan yukarı, görev bazlı tahmin. İş kırılımındaki her görev (`gorev-dagilimi.md`) sahibine
göre saatlendirildi ve aşama aşama toplandı. Sorumluluk bölümü: Kişi A (Atahan) yorumlar, NLP,
açıklanabilirlik, kullanıcı çalışması; Kişi B (Ali Rubar) ürün ve enerji verisi, skorlama, ML, arayüz.
Ortak işler yarı yarıya bölündü. İkisi de diğer derslerle birlikte haftada 5–6 saat çalışıyor.

**Süre:** 15.10.2026 – 25.01.2027, yaklaşık **3,4 ay** (14,5 hafta).

| Aşama | Tarih | Kişi A (saat) | Kişi B (saat) | A'nın ana işleri | B'nin ana işleri |
|---|---|---|---|---|---|
| 0. Keşif ve kararlar | 22.10–31.10 | 8 | 8 | Yorum kaynağı incelemesi, NLP ön araştırması | EPREL erişimi, ürün sayfaları, maliyet varsayımları, ortam kurulumu |
| 1. Veri toplama ve ön işleme | 27.10–10.11 | 16 | 16 | Yorum toplama ve içe aktarma, temizleme, etiketleme kılavuzu | Ürün listesi, EPREL eşleştirme, uçtan uca çalışma, keşifsel veri analizi |
| Ara rapor ve sunum | 10.11–13.11 | 6 | 6 | Literatür, NLP bölümleri | Veri seti, mimari bölümleri |
| 2. NLP ve özellik çıkarımı | 10.11–05.12 | 20 | 16 | Etiketleme (yarısı), BERTurk ince ayarı, hata analizi | Etiketleme (yarısı), TF-IDF, kural sözlüğü, skorlama iyileştirmesi |
| 3. Skorlama modeli | 05.12–31.12 | 12 | 16 | SHAP açıklamaları, yorum kanıtları, ürün etiketleme (yarısı) | AHP, ML karşılaştırması, duyarlılık, ürün etiketleme (yarısı), arayüz |
| 4. Açıklanabilirlik, arayüz, teslim | 01.01–25.01 | 18 | 18 | Kullanıcı çalışması, açıklama API'si, final rapor (yarısı) | Arayüzün son hali, demo, final rapor (yarısı) |
| **Toplam** | | **80** | **80** | | |

**Emek:** 1 kişi-ay = 160 saat (tam zamanlı bir ay) kabulüyle kişi başına 80 / 160 = **0,5 kişi-ay**,
toplam **1,0 kişi-ay**. 80 saat / 14,5 hafta ≈ haftada 5,5 saat; takvim süresi 3,4 ay olduğu için bu,
iki kişinin yaklaşık %15 zamanla çalışmasına karşılık geliyor.

**Maliyet:**

| Kalem | Tahmin | Not |
|---|---|---|
| İnsan kaynağı | 160 saat × saatlik ücret | Saatlik ücret için güncel ve kaynağı gösterilebilir bir değer kullanın (ör. yeni mezun yazılım mühendisi maaş araştırması). Rakamı uydurmayın. |
| Donanım | 0 TL ek maliyet | Kişisel bilgisayarlar. İsterseniz amortisman ekleyin. |
| GPU | 0 TL | Google Colab ücretsiz katmanı (T4). Ücretsiz katman garanti değil; risk tablosunda R7. |
| Yazılım | 0 TL | Python, FastAPI, React, scikit-learn, PyTorch, transformers: açık kaynak |
| Veri | 0 TL | EPREL ve üretici etiketleri herkese açık; mağaza sayfaları elle kaydedildi |
| Barındırma | 0 TL | Demo yerel çalışıyor |

Sonuç: projenin maliyeti fiilen insan kaynağından ibaret.

## 3. Risk analizi (rapor 2.2.7)

**Nasıl yapılır:** Her risk için olasılık ve etki 1–3 arası puanlanır (1 düşük, 2 orta, 3 yüksek). Risk puanı
= olasılık × etki (1–9). Puanı 6 ve üstü olanlar yüksek risk sayılır ve önlemi önceden uygulanır. Rapora
tablonun yanında 3×3'lük bir risk matrisi (olasılık × etki, hücrelerde risk numaraları) konabilir.
"Durum" kolonu bu raporda değerli: bazı riskler gerçekleşti ve nasıl yönetildiği gösterilebilir.

| ID | Risk | O | E | Puan | Önlem | Sorumlu | Durum (11.11) |
|---|---|---|---|---|---|---|---|
| R1 | E-commerce sites block automated collection of reviews | 3 | 3 | 9 | Save pages by hand in a browser, parse them offline; no scraper where forbidden | A | Gerçekleşti, önlemle aşıldı (3.467 yorum) |
| R2 | EPREL public API needs a sealed declaration, data cannot be downloaded in bulk | 3 | 2 | 6 | Collect EPREL records by hand; read official manufacturer labels for the rest | B | Gerçekleşti, aşıldı (48 EPREL + 23 etiket) |
| R3 | Energy data missing for many products | 3 | 2 | 6 | Manufacturer labels, store titles; record the source; report what is left | A, B | Azaltıldı: 32 → 2 eksik |
| R4 | Too few labelled examples for rare aspects (energy, service) | 3 | 2 | 6 | Enriched sampling of the training pool, class-weighted loss, thresholds tuned on validation | A | Açık |
| R5 | Low agreement between annotators | 2 | 3 | 6 | Guideline tested on real reviews, kappa on 100 shared reviews, disagreements decided together | A, B | Açık |
| R6 | BERTurk does not beat simpler methods on a small dataset | 2 | 2 | 4 | Compare all methods on the same test set and report the result as it is | A | Açık |
| R7 | No GPU available for training | 1 | 2 | 2 | Free cloud notebook (Colab T4); base-size model | A | Düşük; deneme çalıştı |
| R8 | Too few products with manual labels for a reliable ML scorer (80 products) | 3 | 2 | 6 | Stratified cross-validation, simple models in the comparison, weighted baseline kept | B | Açık |
| R9 | Product selection bias (e.g. no class-A refrigerator because efficient models have few reviews) | 3 | 2 | 6 | Report as a limitation or add efficient products with fewer reviews | B | Açık, karar bekliyor |
| R10 | Schedule slip or a team member temporarily unavailable | 2 | 3 | 6 | Clear task owners, pull-request reviews, one integration branch that always runs | A, B | Kısmen gerçekleşti |
| R11 | Legal or terms-of-use issues with using review text | 2 | 3 | 6 | No redistribution of review text, no user names, academic use only; ask the advisor | A, B | Açık |
| R12 | Site layout changes break the page parser | 2 | 1 | 2 | Tests on synthetic pages; the parser stops with the file name instead of skipping | A | Düşük |
| R13 | Loss of collected data | 1 | 3 | 3 | Code in Git; raw data backed up outside the repository | A, B | Düşük |

Risk matrisi (hücrelerde risk numaraları):

| Olasılık \ Etki | 1 Düşük | 2 Orta | 3 Yüksek |
|---|---|---|---|
| **3 Yüksek** | | R2, R3, R4, R8, R9 | R1 |
| **2 Orta** | R12 | R6 | R5, R10, R11 |
| **1 Düşük** | | R7 | R13 |
