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

## Açık sorular

- [ ] Elektrik ve su birim fiyatları hangi tarifeden alınacak? (`config/categories.yaml`)
- [ ] Ürün ömrü varsayımları (buzdolabı 12, çamaşır makinesi 10 yıl) için kaynak.
- [ ] EPREL API anahtarı gerekiyor mu, yoksa toplu indirme yeterli mi?
- [ ] Hangi site? Trendyol, Hepsiburada veya ikisi.
