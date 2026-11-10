# Diyagramlar (rapor ve sunum için)

Rapor İngilizce olduğu için diyagram etiketleri İngilizcedir. Hepsi koddaki gerçek modül, tablo ve
komut adlarıyla yazıldı (10.11.2026, `demo/entegrasyon` dalındaki durum).

- **Mermaid** blokları GitHub'da doğrudan çizilir. PNG/SVG için https://mermaid.live adresine
  yapıştırıp "Export" kullanın.
- **PlantUML** blokları (UML use case ve sequence) GitHub'da çizilmez. https://www.planttext.com
  adresine yapıştırıp PNG/SVG alın.
- Raporda her diyagramın altına şekil numarası ve açıklama gerekir (hoca diyagramların metinde
  yeterli ayrıntıyla açıklanmasını istiyor). Aşağıdaki "Ne gösteriyor" notları bunun için.

Mimari diyagramının Türkçe sürümü: `architecture.md`.

## 1. Use case diyagramı (rapor 2.2.3)

Ne gösteriyor: Sistemin iki tür kullanıcısı var. **Shopper** (alışveriş yapan kullanıcı) arayüzü
kullanır; **Project team** (geliştirici/analist) verileri toplar, etiketler ve modeli çalıştırır.
EPREL ve e-ticaret siteleri dış sistemlerdir; yorumlar kullanıcı tarafından tarayıcıdan kaydedilen
sayfalardan okunur (otomatik toplama yok).

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
actor Shopper
actor "Project team" as Team
actor "EPREL database" as EPREL <<external>>
actor "E-commerce site" as Shop <<external>>

rectangle "GreenChoice" {
  usecase "Browse products\nby category" as UC1
  usecase "View score, label\nand explanations" as UC2
  usecase "Compare 2-4 products" as UC3
  usecase "Adjust criterion\nweights" as UC4
  usecase "Search products" as UC5
  usecase "Collect product and\nenergy data" as UC6
  usecase "Import saved\nreview pages" as UC7
  usecase "Annotate reviews\n(aspect, polarity)" as UC8
  usecase "Train and evaluate\nNLP models" as UC9
  usecase "Build scores\n(pipeline)" as UC10
  usecase "Set weights with AHP" as UC11
}

Shopper --> UC1
Shopper --> UC5
Shopper --> UC3
Shopper --> UC4
UC1 ..> UC2 : <<include>>
UC3 ..> UC2 : <<include>>
UC4 ..> UC2 : <<include>>

Team --> UC6
Team --> UC7
Team --> UC8
Team --> UC9
Team --> UC10
Team --> UC11
UC6 --> EPREL
UC6 --> Shop
UC7 --> Shop
UC10 ..> UC9 : <<include>>
@enduml
```

## 2. Sistem mimarisi (rapor 4.3.1)

Ne gösteriyor: İki parça. **Offline pipeline** bütün hesaplamayı yapar ve sonucu tek bir SQLite
dosyasına yazar. **Servis** (FastAPI + React) yalnızca bu dosyayı okur; tek canlı hesap, kullanıcının
ağırlıkları değiştirdiğinde yapılan ağırlıklı toplamdır. Bu yüzden API hızlı ve basittir, canlı
scraping veya model çıkarımı yoktur.

```mermaid
flowchart LR
    subgraph Sources
        EC["E-commerce pages<br/>saved by hand"]
        EP["EPREL records<br/>collected by hand"]
        XL["Data collection<br/>workbook (xlsx)"]
    end
    subgraph Pipeline["Offline pipeline: greenchoice build"]
        IM["collect<br/>import-sheets, import-reviews"] --> PR["preprocess<br/>cleaning, EPREL matching, TCO"]
        PR --> NL["nlp<br/>AspectExtractor:<br/>rule / TF-IDF / BERTurk"]
        NL --> AG["nlp.aggregate<br/>product review features"]
        PR --> CR["scoring.criteria<br/>6 criteria in 0-1"]
        AG --> CR
        CR --> SC["scoring<br/>weighted (AHP weights) / ML"]
        SC --> EX["explain<br/>contributions to Turkish text"]
    end
    EC --> IM
    EP --> IM
    XL --> IM
    EX --> DB[("SQLite<br/>greenchoice.db")]
    PR --> DB
    NL --> DB
    DB --> API["FastAPI<br/>7 endpoints under /api"]
    API --> UI["React UI<br/>list, detail, compare,<br/>weight sliders"]
```

## 3. Veri akışı ve kriterler (rapor 4.2 "How the system works")

Ne gösteriyor: Bir ürünün skoruna giden yol. Yapısal veriden (fiyat, enerji, su) toplam maliyet;
yorumlardan aspect bazlı duygular; ikisinden altı kriter; ağırlıklı toplamdan skor ve etiket;
kriter katkılarından açıklama cümleleri.

```mermaid
flowchart TB
    P["Product data<br/>price, energy class,<br/>kWh, water, rating"] --> T["TCO = price + years x<br/>(kWh x TL/kWh + m3 x TL/m3)"]
    R["Reviews"] --> CL["Cleaning<br/>normalise, drop spam,<br/>mask delivery phrases"]
    CL --> AX["Aspect extraction<br/>durability, energy, service,<br/>failure, noise x pos/neg"]
    AX --> AGG["Per product:<br/>durability score,<br/>service issue rate"]
    P --> C1["Energy efficiency"]
    T --> C2["Lifetime cost"]
    AGG --> C3["Durability"]
    AGG --> C4["Service"]
    P --> C5["Price advantage"]
    P --> C6["Satisfaction<br/>(Bayesian rating)"]
    C1 & C2 & C3 & C4 & C5 & C6 --> W["Weighted sum<br/>(category weights)"]
    W --> S["Score 0-100<br/>label: recommended / neutral / not recommended"]
    W --> E["Contribution of each criterion<br/>vs category mean"]
    E --> X["Explanation sentences<br/>(imputed criteria are not explained)"]
```

## 4. Sıralama diyagramı: ürün detayı ve özel ağırlık (rapor 4.2)

Ne gösteriyor: Kullanıcı bir kategori seçer, ürün detayını açar ve ağırlıkları değiştirir. Detay ve
açıklama önceden hesaplanmış olarak veritabanından gelir; özel ağırlıkta API skorları yeniden
hesaplar (yalnızca ağırlıklı toplam ve açıklamalar), pipeline yeniden çalışmaz.

```plantuml
@startuml
actor Shopper
participant "React UI" as UI
participant "FastAPI" as API
database "SQLite" as DB

Shopper -> UI : select category
UI -> API : GET /api/products?category=refrigerator
API -> DB : read products + scores
DB --> API : rows
API --> UI : list (score, label)
Shopper -> UI : open product
UI -> API : GET /api/products/{id}
API -> DB : read product, features, score
API --> UI : detail (sub-scores, TCO, explanations)
Shopper -> UI : move weight sliders
UI -> API : POST /api/score {category, weights}
API -> DB : read product_features
API -> API : weighted sum + explanations\n(score_products)
API --> UI : re-ranked list
@enduml
```

## 5. Sınıf diyagramı: genişletme noktaları (rapor 4.3)

Ne gösteriyor: Yöntemler ortak arayüzlerin arkasında değişebilir. Yeni bir NLP yöntemi
`AspectExtractor`'dan türetilir; `build --nlp` hangisinin kullanılacağını seçer.

```mermaid
classDiagram
    class AspectExtractor {
        <<abstract>>
        +method: str
        +extract(text_clean) list~AspectMention~
        +extract_df(reviews, column) DataFrame
    }
    class RuleBasedExtractor {
        +method = "rule_based_v0"
        -patterns from config/aspects.yaml
    }
    class TfidfExtractor {
        +method = "tfidf_lr_v0"
        +train(texts, y)
        +predict_proba(texts)
        +save(path) / load(path)
    }
    class TransformerExtractor {
        +method = "berturk_v0"
        +predict_proba(texts)
        -thresholds from thresholds.json
    }
    class AspectMention {
        +aspect: str
        +polarity: pos or neg
        +evidence: str
    }
    class WeightedScorer {
        +method = "weighted_v0"
        +weights_for(category, override)
        +score(criteria) DataFrame
    }
    class ProductSource {
        <<abstract>>
        +iter_product_urls(category, max)
        +fetch_product(url, category)
        +fetch_reviews(product, max)
    }
    AspectExtractor <|-- RuleBasedExtractor
    AspectExtractor <|-- TfidfExtractor
    AspectExtractor <|-- TransformerExtractor
    AspectExtractor ..> AspectMention
```

## 6. Veritabanı şeması (rapor 4.3)

Ne gösteriyor: Pipeline'ın yazdığı beş tablo ve ilişkileri. Kolonların bir kısmı gösterildi;
`product_features` 46 kolonlu bir özellik tablosudur (ham özellikler + yorum özellikleri + kriterler).

```mermaid
erDiagram
    products ||--o{ reviews : has
    reviews ||--o{ review_aspects : yields
    products ||--|| product_features : "described by"
    products ||--o{ scores : "scored by method"
    products {
        text product_id PK
        text category
        text brand
        text model_code
        real price_tl
        text energy_class
        real annual_kwh
        real tco_tl
        int eprel_matched
    }
    reviews {
        text review_id PK
        text product_id FK
        int rating
        text text_clean
        text text_product
        int mentions_logistics
    }
    review_aspects {
        text review_id FK
        text aspect
        text polarity
        text method
        text evidence
    }
    product_features {
        text product_id PK
        int n_reviews
        real durability_score
        real service_issue_rate
        real c_energy_efficiency
        real c_lifetime_cost
        text imputed
    }
    scores {
        text product_id FK
        text method
        real score
        text label
        text sub_scores_json
        text explanations_json
    }
```

## 7. NLP iş akışı: etiketlemeden modele (rapor 3.2 / 4.3)

Ne gösteriyor: Elle etiketleme ve model eğitiminin adımları. Test seti yalnızca son raporlamada
bir kez kullanılır; eşikler doğrulama (val) setinde ayarlanır.

```mermaid
flowchart LR
    RV["3,467 reviews<br/>(73 products)"] --> PL["annotation-pool<br/>100 random test +<br/>300 enriched train"]
    PL --> SH["Two sheets<br/>A: 250, B: 250<br/>(100 shared)"]
    SH --> CLB["collect-labels<br/>value checks, kappa,<br/>disagreements"]
    CLB --> GD["Gold labels<br/>train / val / test"]
    GD --> RB["Rule-based"]
    GD --> TF["train-nlp<br/>TF-IDF + LR"]
    GD --> BT["Colab<br/>BERTurk fine-tune"]
    RB & TF & BT --> EV["Same test set:<br/>P / R / F1"]
```
