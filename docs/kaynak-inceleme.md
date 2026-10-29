# Kaynak incelemesi

Her bilgi için kaynağı ve doğrulama durumu yazılır. "Doğrulanmadı" yazan satırlar koda
sabit değer olarak girmez.

## EPREL (Kişi B · B0.1)

İnceleme tarihi: 29.10.2026. Kaynak: EPREL'in resmi
[Request Public API Key](https://eprel.ec.europa.eu/screen/requestpublicapikey) sayfası
(tarayıcıda açılıp okundu), aşağıdaki not edilenler dışında.

### Doğrulananlar

| Konu | Bulgu | Kaynak |
|---|---|---|
| Public API var mı | Evet. "Modellerin public verisine programatik erişim" sağlayan web servisleri | Resmi sayfa |
| Anahtar gerekli mi | **Evet.** Modelleri aramak ve getirmek için API anahtarı gerekiyor | Resmi sayfa |
| Anahtar nasıl alınır | 1) Formu doldur ve "EPREL Declaration" indir. 2) Beyanı **elektronik mühür veya dijital imza** ile imzala. 3) İmzalı beyanı sayfada belirtilen e-posta adresine gönder | Resmi sayfa |
| Form alanları | Company/Individual, organisation name, legal representative, contact email, use of data, application name, application URL, şartların kabulü | Resmi sayfa |
| Şartlar belgesi | [API_TERMS_AND_CONDITIONS_EN.pdf](https://ec.europa.eu/assets/move-ener/eprel/EPREL%20Public/Public%20API%20Term%20and%20Conditions/API_TERMS_AND_CONDITIONS_EN.pdf) | Resmi sayfadaki bağlantı |
| Yardım masası | ENER-EPREL-HELPDESK@ec.europa.eu (şartlar PDF'inde `mailto` olarak görünüyor) | PDF yapısı |
| Ürün sayfası örüntüsü | `https://eprel.ec.europa.eu/screen/product/<grup>/<id>` ve `https://eprel.ec.europa.eu/fiches/<grup>/Fiche_<id>_EN.pdf` | Arama sonuçlarında görülen gerçek adresler |
| Buzdolabı grup adı | `refrigeratingappliances2019` bir fiş adresinde geçiyor, `categories.yaml`'daki değerle uyumlu | Aynı |
| Ürün sayfası etiketi | Sayfalarda yıllık tüketim "Annual energy consumption (kWh/annum)" olarak yazıyor | Arama sonuçları |

### Doğrulanmadı

- API'nin taban adresi. `https://eprel.ec.europa.eu/api` yalnızca üçüncü taraf bir PHP
  istemcisinde ve koddaki tahminde geçiyor.
- JSON alan adları (`energyClass`, `energyConsAnnual`, ...). `collect/eprel.py` içindeki
  `FIELD_MAP` hâlâ tahmin. Üç farklı aramada resmi şema bulunamadı.
- `washingmachines2019` grup adı. Yalnızca buzdolabı grubu görüldü.
- Toplu indirme seçeneği. Yapılan aramalarda bulunamadı, bu "yok" demek değil.
- Şartlar PDF'inin içeriği (kullanım sınırları, yeniden dağıtım, atıf). Metin
  otomatik okunamadı, **elle okunmalı**.
- Resmi API dokümantasyonu `webgate.ec.europa.eu` altında. Adresi alınamadı. Bir
  EPREL kılavuzuna göre geliştirici wiki'si EU Login ister (ikinci el bilgi).

### Engel ve seçenekler

Anahtar için **imzalı beyan** şart. Türkiye'de e-imza veya mühür her öğrencide yoktur.

1. Okul veya danışman kurumsal bir imza/mühür sağlayabilir mi? Danışmana sorulacak
   (31.10 toplantısı gündemi).
2. Yardım masasına, öğrenci projesi için alternatif yol olup olmadığı sorulabilir.
3. Yedek plan: ürün sayfalarından elle toplama (B0.2'deki 20 ürünlük deneme zaten elle).
   EPREL'in kullanım koşulları bunu serbest bırakıyor mu, şartlar PDF'ine bakılarak
   netleşmeden otomatik toplama yapılmayacak.
4. Yedek veri: karar #2'deki Amazon Reviews 2023, ama enerji verisi içermez.

Anahtar gelene kadar `EprelClient.search_model` yazılmaz. Pipeline, EPREL verisini
bir CSV olarak okumaya zaten hazır (`merge_eprel`).
