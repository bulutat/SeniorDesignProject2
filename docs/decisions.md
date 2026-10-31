# Karar kaydı

Önemli kararlar buraya tarihle yazılır. Bir karar değişirse eskisi silinmez,
"yerine geçti" notu düşülür. Rapordaki "Yöntem" bölümü için kaynak olur.

| # | Tarih | Karar | Gerekçe | Durum |
|---|---|---|---|---|
| 1 | 22.10.2026 | Kategoriler: buzdolabı ve çamaşır makinesi | Enerji belirleyici, yorum çok, EPREL verisi var; kriter ağırlıkları farklı | Öneri, danışmanla teyit |
| 2 | 22.10.2026 | Kaynak: Türk e-ticaret sitesi + EPREL (model koduyla eşleştirme). Yedek: Amazon Reviews 2023 | Türkçe veri özgünlük katar; enerji verisi resmi kaynaktan gelir | Öneri |
| 3 | 22.10.2026 | Dil: Türkçe, BERTurk (`dbmdz/bert-base-turkish-cased`) | Türkçe için yaygın ve erişilebilir model | Öneri |
| 4 | 22.10.2026 | 6 kriter: enerji verimliliği, uzun vadeli maliyet, dayanıklılık, servis/arıza, fiyat avantajı, memnuniyet | Hem yapılandırılmış hem yorum verisi skora katkı verir | Öneri |
| 5 | 22.10.2026 | Ground truth: ~150–200 ürün, iki kişi bağımsız 3 sınıf etiket, Cohen's kappa | Proposal'daki "manuel değerlendirmeyle uyum" kriteri | **Danışmanla teyit edilecek** |
| 6 | 22.10.2026 | Mimari: offline batch pipeline + SQLite + FastAPI + React | Prototip kapsamı; API basit ve hızlı kalır | Kabul |
| 7 | 22.10.2026 | Baseline: kategoriye özel ağırlıklı toplam (weighted_v0), ML modelleri bununla karşılaştırılır | Hoca metninde açıkça isteniyor | Kabul |
| 8 | 22.10.2026 | Eksik kriter verisi kategori medyanıyla doldurulur, açıklamada kullanılmaz | Eksik veri yüzünden yanlış açıklama üretmemek | Kabul |
| 9 | 22.10.2026 | Görev dağılımı rev. 2: ML model karşılaştırması A'dan B'ye geçti; A NLP ve açıklanabilirliğe odaklanır | İskelet B'nin görevlerinin çoğunu bitirdi, yük dengelendi. Ayrıntı: `gorev-dagilimi.md` | Kabul, isimler atanacak |
| 10 | 30.10.2026 | Su birim fiyatı: İSKİ 2026 konut tarifesi, 0–15 m³/ay kademesi, su 43,70 + atık su 21,82 = **65,52 TL/m³, KDV hariç**. Referans şehir İstanbul | Resmi İSKİ sayfasından okundu. Haber sitelerindeki 52,88 TL rakamı bu sayfayla uyuşmadı, kullanılmadı. Çamaşır makinesi yılda ~11 m³ su kullandığı için aylık 15 m³ kademesi geçerli. "İnsani su hakkı" (aylık 15 m³'e kadar tüketimin %20'si faturalanmaz) modele katılmadı, bu TCO'yu hafif yüksek gösterir | Kabul, danışmanla teyit |
| 11 | 30.10.2026 | *(Yerine karar 15 geçti.)* Elektrik birim fiyatı **doğrulanamadı**, 3,0 TL/kWh yer tutucu olarak kaldı | Resmi EPDK mesken tablosu okunamadı. İkincil kaynaklar çelişiyor: kademe 1 / kademe 2 için 2,92 / 4,32 TL (KDV hariç, Nisan 2026 dönemi gibi) ve başka bir kaynakta 3,24 / 4,86 TL (vergili görünüyor, resmî olduğu belirtilmemiş). Tarifeler üç ayda bir (Ocak, Nisan, Temmuz, Ekim) güncelleniyor, Ekim 2026 kararı doğrulanamadı | **Açık** |
| 12 | 30.10.2026 | Ürün ömrü: çamaşır makinesi 12 yıl (önceki varsayım 10), buzdolabı 12 yıl (kaynaksız) | Çamaşır makinesi için: bir inceleme makalesi Eko-tasarım hazırlık çalışmalarında 12,5 yıl kullanıldığını yazıyor; JRC onarım verisi onarılmayan cihazlarda ortalama 12,6 yıl veriyor (ikisi de arama özetinden, birincil kaynak okunmadı). Buzdolabı için AB kaynağı bulunamadı; tüketici kuruluşu çalışması (Choice, Avustralya) orta sınıf için 9, üst sınıf için 13 yıl diyor. 12 yıl kaynaksız bir varsayım | Kabul, buzdolabı için kaynak aranacak |
| 13 | 30.10.2026 | Yılda 220 yıkama varsayımı korundu | Yönetmelik (AB) 2019/2023 Ek V'te yıllık su tüketimi 220 yıkama üzerinden hesaplanıyor ([legislation.gov.uk](https://www.legislation.gov.uk/eur/2019/2023/annex/V)). Etiket Yönetmeliği 2019/2014'te yıllık dönüşüm formülünü doğrulayamadık | Kabul |
| 14 | 30.10.2026 | Bilinen sınır: TCO'da mağaza fiyatı (KDV dahil) ile işletme maliyetleri (KDV hariç) toplanıyor | Su fiyatı KDV hariç yayımlanıyor, elektrik için durum belirsiz; KDV oranlarını doğrulamadık, uydurmadık | Raporda belirtilecek |
| 15 | 01.11.2026 | Elektrik birim fiyatı: **2,919 TL/kWh, vergiler hariç** (mesken, alçak gerilim tek zamanlı, günlük ortalama 8 kWh ve altı kademe). Yüksek kademe (8 kWh/gün üstü) 4,321 TL/kWh | EPDK Kurul Kararı 14461 (02/04/2026), 4 Nisan 2026'dan itibaren geçerli "Vergiler Hariç Elektrik Tarifeleri" tablosu (Resmî Gazete 4 Nisan 2026, sayı 33214). Tablo notuna göre perakende tarife = enerji bedeli + dağıtım bedeli: düşük kademe 49,4065 + 242,49 = 291,8965 kr/kWh, yüksek kademe 189,5808 + 242,49 = 432,0708 kr/kWh. Düşük kademe seçildi, çünkü tipik bir hane günde ortalama 8 kWh'in altında kalıyor varsayıldı (bu varsayım doğrulanmadı). Duyarlılık analizinde (B3.3) yüksek kademe de denenecek. **Dönem Nisan 2026'dır, daha yeni bir karar (Temmuz/Ekim) olup olmadığı doğrulanmadı** | Kabul, güncel dönem teyit edilecek |


- [x] Elektrik birim fiyatı: Nisan 2026 tablosundan alındı, karar 15.
- [ ] Nisan 2026'dan sonra (Temmuz veya Ekim 2026) yeni bir EPDK tarife kararı var mı? Varsa karar 15 güncellenir.
- [ ] Hane tüketimi günde 8 kWh'in altında mı üstünde mi varsayılacak (düşük/yüksek kademe)? Danışmanla konuş.
- [x] Su birim fiyatı: İSKİ 2026 konut tarifesi, karar 10.
- [ ] Buzdolabı ömrü için kaynak (çamaşır makinesi için karar 12).
- [x] EPREL API anahtarı gerekiyor mu, yoksa toplu indirme yeterli mi? **Anahtar gerekiyor**
  ve elektronik mühür/dijital imzalı beyan istiyor; toplu indirme bulunamadı.
  Ayrıntı ve seçenekler: `kaynak-inceleme.md`.
- [ ] EPREL anahtarı için imza/mühür kim sağlayacak? (31.10 danışman toplantısı)
- [ ] Hangi site? Trendyol, Hepsiburada veya ikisi.
