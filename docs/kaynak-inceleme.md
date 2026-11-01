# Kaynak incelemesi

Her bilgi için kaynağı ve doğrulama durumu yazılır. "Doğrulanmadı" yazan satırlar koda
sabit değer olarak girmez.

## Yorumlar (Kişi A · A0.1)

İnceleme tarihi: 01.11.2026. Yalnızca yapı incelendi: robots.txt, kullanım koşulları ve pilot
listeden birer ürün sayfası normal tarayıcıda açıldı. Yorum verisi toplanmadı ve repoya eklenmedi.

**Sonuç:** İki sitede de otomatik yorum toplamaya uygun bir yol bulunamadı. Scraper yazılmadı;
robots.txt veya bot koruması aşılmayacak (`AGENTS.md`). Yerine yorum sayfaları tarayıcıdan elle
kaydedilip yerelde okunuyor: [yorum-toplama.md](yorum-toplama.md). Kullanım koşulları sorusu bu
yöntemde de açık, danışmana sorulacak.

### Trendyol

| Konu | Bulgu | Durum |
|---|---|---|
| Ürün yorum sayfası | `/<marka>/<ürün>-p-<id>/yorumlar` açılıyor; `www.trendyol.com/robots.txt` bu yolu yasaklamıyor | Doğrulandı |
| Yorumların yüklenmesi | Sayfanın HTML'inde yorum yok (`productReviews: null`). Yorumlar tarayıcıda sonradan, kaydırdıkça 20'şer yükleniyor. HTML'de `apigw.trendyol.com` altında `review-detail` ve `product-reviews-seo` adresleri geçiyor | İstek ağ kaydında görülemedi; adres HTML'den okundu |
| `apigw.trendyol.com/robots.txt` | `User-agent: *` için `Disallow: /` | Doğrulandı. **Engel** |
| `www.trendyol.com/robots.txt` | `/gw/` yasak. Diğer dillerde `/get/api/review/*` ve `/reviews` yasak | Doğrulandı |
| Kullanım koşulları | `/kullanim_kosullari`: site materyalleri önceden izin alınmadan ve kaynak gösterilmeden kopyalanamaz, çoğaltılamaz, başka bilgisayara yüklenemez. Kullanıcı yorumlarının bu kapsamda olup olmadığı açıkça yazmıyor | Metin okundu, hukuki yorum yapılmadı |
| Sayfa içi veri | `__review-detail__PROPS`: ortalama puan, puan ve yorum sayısı, teknik özellikler (örnek ürün: 4,6 · 108 değerlendirme · 64 yorum) | Doğrulandı |

### Hepsiburada

| Konu | Bulgu | Durum |
|---|---|---|
| Otomatik istek | `robots.txt`, proje `User-Agent`'ı ile istendiğinde **403** ve güvenlik/CAPTCHA sayfası döndü. Normal tarayıcıda açıldı | Doğrulandı. **Engel** (`PoliteClient`, 403 alınan robots.txt'de hiçbir adrese izin vermez) |
| robots.txt | `/api/` ve `/product-comment/` yasak. `product-review` site haritası var, `-yorumlari` ile biten sayfalar yasaklı görünmüyor | Doğrulandı |
| Yorum sayfası | `<ürün>-pm-<id>-yorumlari` açılıyor, yorumlar sayfa HTML'inde. Puan alt başlıkları da var: Yıkama, Sessiz Çalışma, Enerji Tüketimi, Program | Doğrulandı (normal tarayıcıda) |
| Kullanım koşulları | `/uyelik-sozlesmesi` giriş sayfasına yönlendiriyor, metin okunamadı | **Doğrulanmadı** |

### Seçenekler

1. **Elle toplama:** EPREL'de olduğu gibi yorumlar tarayıcıdan elle Excel'e alınır. Yorum sayısı
   düşük ürünlerde mümkün, 80–100 ürün/kategori için zor. Koşullar açısından danışmana sorulmalı.
2. **Site izni:** Danışman veya bölüm üzerinden Trendyol/Hepsiburada'dan akademik izin veya veri
   istenir. Temiz yol ama süre belirsiz.
3. **Hazır veri seti, yorum modeli için:** [MüşteriYorumları](https://huggingface.co/datasets/turkish-nlp-suite/MusteriYorumlari)
   (Hepsiburada ve Trendyol, ~104 bin yorum, CC-BY-SA-4.0). Yalnızca `text` ve yıldız etiketi var;
   ürün veya kategori bilgisi yok, bu yüzden pilot ürünlerle **eşleştirilemez**. BERTurk
   ön eğitimi için kullanılabilir, ürün skorlaması için yetmez. Veri setinin toplanma
   koşulları doğrulanmadı. Beyaz eşya odaklı Türkçe etiketli ABSA veri seti aramalarda bulunamadı.
4. **Amazon Reviews 2023:** Karar #2'deki yedek. İngilizce; enerji sınıfı yok, dil ve model değişir.

### Doğrulanmadı

- Trendyol yorum isteğinin tam adresi, parametreleri ve JSON alanları. Engel nedeniyle araştırılmadı.
- Seçilecek site. Elle toplamada Hepsiburada sayfası daha uygun görünüyor (21/26 pilot ürün,
  yorumlar HTML'de), ama bu yalnızca tek ürünle bakıldı.

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
- Toplu indirme seçeneği. Yapılan aramalarda bulunamadı, bu "yok" demek değil.
- Şartlar PDF'inin içeriği (kullanım sınırları, yeniden dağıtım, atıf). Metin
  otomatik okunamadı, **elle okunmalı**.
- Resmi API dokümantasyonu `webgate.ec.europa.eu` altında. Adresi alınamadı. Bir
  EPREL kılavuzuna göre geliştirici wiki'si EU Login ister (ikinci el bilgi).

### Elle arama ve etiketler (30.10.2026'da denendi)

| Konu | Bulgu |
|---|---|
| Arama | Grup sayfasında (`/screen/product/washingmachines2019`, `/screen/product/refrigeratingappliances2019`) "Model identifier / Brand or trademark / Model commercial name / GTIN" seçenekli arama var. Model arama **tam eşleşme** istiyor (`GNWM` bulunamadı, tam kod bulundu) |
| Eski ürünler | "Include models not placed on the market anymore" kutusu işaretlenmezse piyasadan çekilmiş modeller görünmez |
| Çamaşır makinesi etiketleri | `Weighted energy consumption (per 100 cycles, eco 40-60 programme)` kWh, `Water consumption (per cycle, eco 40-60 programme)` litre, `Airborne acoustical noise emissions (spinning phase)` dB, `Rated capacity` kg. "Energy consumption (per cycle...)" satırını **alma** |
| Buzdolabı etiketleri | `Annual energy consumption` kWh/annum, `Airborne acoustical noise emissions` dB(A), `Total volume` litre |
| Enerji sınıfı | Metinde harf yok. Etiket görselinin dosya adından okunuyor (`.../label/thumbnails/A-Left-DarkGreen-...svg`). Buzdolabı sayfasında ışık kaynağı için ayrı bir "Energy efficiency class" satırı var, onunla karıştırma |
| Grup adları | `washingmachines2019` ve `refrigeratingappliances2019` gerçek sayfalarda doğrulandı |

### Mağaza kodu ile EPREL kodu eşleşmesi (marka bazında deneme)

Hepsiburada listelerinden alınan kodlar EPREL'de tam eşleşmeyle denendi. Sonuçlar seçim yanlılığı taşır, genel oran değildir.

| Marka | Denenen | Bulunan | Not |
|---|---|---|---|
| Bosch | 5 + 12 buzdolabı | tümü | Türkiye ve AB kodları aynı |
| Siemens | 12 + 9 buzdolabı | tümü | Aynı grup (BSH) |
| Samsung | 5 çamaşır makinesi, 11 buzdolabı | 5 / 1 | Çamaşır makinesinde mağaza kodundaki sondaki `AH` eki kesilince bulunuyor. Buzdolabında 11 kodun yalnızca 1'i |
| LG | 6 çamaşır makinesi | 2 | |
| Beko | 8 çamaşır makinesi | 0 | EPREL'de Beko kayıtları var ama `B1WFM2841GBEE 8786033200` gibi AB kodlarıyla; Türkiye adı (`CMX 12140`) eşleşmiyor |
| Grundig | 1 çamaşır makinesi | 0 | EPREL'de 153 Grundig kaydı var, kodlar `GW9P69416W 7006740004` biçiminde; `GNWM 91613 RS` yok |

Sonuç: eşleşme markaya ve Türkiye'ye özgü model adlarına bağlı. Barkod (GTIN) ile eşleştirme denenmedi.

### Elektrik tarifesi (EPDK, 01.11.2026'da okundu)

Kaynak: EPDK Kurul Kararı **14461**, 02/04/2026; ekindeki "4 Nisan 2026 Tarihinden İtibaren
Geçerli Vergiler Hariç Elektrik Tarifeleri" tablosu (Resmî Gazete 4 Nisan 2026, sayı 33214).
Karar metni ve tablo ayrı dosyalar olarak indirildi; fiyatlar tablodadır.

| Satır (AG Tek Terim) | Tek zamanlı enerji bedeli | Dağıtım bedeli | Toplam |
|---|---|---|---|
| Mesken, 8 kWh/gün ve altı | 49,4065 kr/kWh | 242,49 kr/kWh | 291,8965 kr/kWh = **2,919 TL/kWh** |
| Mesken, 8 kWh/gün üstü | 189,5808 kr/kWh | 242,49 kr/kWh | 432,0708 kr/kWh = **4,321 TL/kWh** |

Tablo notları: perakende tarife (vergiler hariç) enerji bedeli ile dağıtım bedelinin toplamıdır;
günlük ortalama 8 kWh'e kadar olan tüketime düşük kademe, aşan kısma yüksek kademe uygulanır.
Birim kuruş/kWh'tir (100 kr = 1 TL). Bu dönem Nisan 2026'dır; sonraki dönemler doğrulanmadı.

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
