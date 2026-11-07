# Etiketleme kılavuzu (taslak)

Sorumlu: Kişi A taslak hazırlar, 07–10.11.2026 arasında birlikte kesinleştirilir.
Etiketleme başladıktan sonra kural değişirse önceki etiketler de güncellenir.

## 1. Yorum etiketleme (aspect + duygu)

Her yorum için içinde geçen **her aspect'i** ve duygusunu (`pos` / `neg`) işaretleyin.
Bir yorumda birden çok aspect olabilir. Hiçbiri yoksa yorumu boş etiketle geçin.

Etiketlemede **yalnızca metne bakın**. Yıldız puanı etiket değildir: 5 yıldızlı bir yorum
"makine çok sesli" diyorsa `noise:neg` olur.

| Aspect | Olumlu (pos) | Olumsuz (neg) | Neyi kapsar |
|---|---|---|---|
| `durability` dayanıklılık | "2 yıldır sorunsuz çalışıyor", "çok sağlam yapılmış" | "3 ayda bozuldu", "kapağı kırıldı", "kısa sürede paslandı" | Ürünün zamana ve kullanıma dayanması |
| `energy` enerji tüketimi | "faturam düştü", "az elektrik yakıyor", "enerji tasarrufu çok iyi" | "çok elektrik harcıyor", "faturam arttı" | Elektrik tüketimi ve fatura etkisi, su tasarrufu dahil |
| `service` servis | "servis hemen geldi", "kurulum ekibi çok ilgiliydi" | "servis gelmedi", "parça yok", "servis çözemedi" | Yetkili servis, kurulum, tamir, garanti işlemi |
| `failure` arıza | — | "hata kodu verdi", "soğutmuyor", "ürün bozuk çıktı" | Çalışmayı etkileyen belirli bir kusur. Olumlu karşılığı yoktur |
| `noise` gürültü | "çok sessiz", "sesi hiç yok" | "gürültülü", "uğultu yapıyor", "titreşiyor" | Çalışma sesi ve titreşim |

### Temel kurallar

1. **Açık ifade şartı.** Yorumcu söylemiyorsa çıkarım yapmayın. "Güzel ürün", "tavsiye ederim",
   "2 aydır kullanıyoruz, güzel cihaz" hiçbir aspect değildir.
2. **Yorum düzeyinde etiket.** Aynı (aspect, polarity) bir yorumda bir kez yazılır. Bir aspect için
   iki yön de geçiyorsa ikisi de yazılır: "kurulum hızlıydı ama arızayı çözemediler" →
   `service:pos` + `service:neg`.
3. **Olumsuzlama:** "hiç bozulmadı" → `durability:pos`; "sessiz değil" → `noise:neg`.
4. **Beklenti ve tahmin etiketlenmez:** "inşallah uzun ömürlü olur", "bozuk galiba" gibi kesin
   olmayan ifadeler yazılmaz. Bu cümledeki başka kesin bilgiler yine yazılır.
5. **Yalnızca bu ürün:** Eski makine, başka marka veya başkalarının yorumları etiketlenmez.
   "Eskisini 15 yıl kullandım" dayanıklılık değildir.
6. **Zamanla değişen deneyim:** Son durum esas alınır. "İlk yıl sorunsuzdu, sonra bozuldu" →
   `durability:neg` + `failure:neg`.

### Sık karışan durumlar

Pilot denemede (01.11.2026, zor durumlar seçilerek 32 gerçek yorum) çıkan kararlar. Örnekler
uydurmadır; gerçek yorumlar repoya yazılmaz.

| Durum | Örnek | Etiket |
|---|---|---|
| Teslimat övgüsü | "Sorunsuz ve sağlam geldi" | Yok. Ürünün dayanıklılığı değil |
| Kısa süre, sorunsuz | "Şimdilik sorunsuz", "yeni aldık sorun yok" | Yok. Açık süre belirtilmemiş |
| Süre + sorunsuz | "6 aydır sorunsuz çalışıyor" | `durability:pos` (alt süre: aşağıdaki açık soru) |
| Süre + arıza | "2 ayda 3 kez arızalandı" | `failure:neg` + `durability:neg` |
| Süre olmadan arıza | "Makine hata kodu veriyor" | `failure:neg` |
| Görsel hasar | "Yan tarafı göçük geldi", "kapağı çizik" | Yok. Çalışmayı etkilemiyorsa nakliye hasarıdır |
| Kırık parça | "Sepet kolu ilk haftada kırıldı" | `durability:neg` |
| Kusur + ses | "Ürün bozuk, çok yüksek ses çıkarıyor" | `failure:neg` + `noise:neg` |
| Yalnızca ses | "Biraz sesli çalışıyor" | `noise:neg` |
| Servis işlemi anılmış, yorum yok | "Servis kaydı açtık", "servis kurdu" | Yok. Olumlu veya olumsuz değerlendirme gerekir |
| Kurulum övgüsü | "Servis aynı gün gelip kurdu, çok ilgiliydiler" | `service:pos` |
| Satıcı veya kargo ilgisi | "Satıcı çok ilgiliydi", "kargocu kaba" | Yok |
| Teslimat ve kurulum tek cümlede | "Hızlı teslimat ve kurulum oldu" | `service:pos` (kurulum kısmı için) |
| Enerjiyle ilgisiz sözcük | "Elektrik kablosu kısa", "faturayı yanlış kesmişler" | Yok |
| Program veya yıkama süresi | "Az su alıyor, temiz yıkamıyor" | Yok. Kaynak tasarrufundan söz edilmiyorsa enerji değil |
| Marka veya mağaza adı | "XYZ Dayanıklı Tüketim'den aldım" | Yok |

Etiketlenmeyen konular: fiyat, iade, fatura, kapasite, ölçü, tasarım, yıkama ve soğutma performansı.
Emin değilseniz boş bırakmayın: `note` sütununa yazın, haftalık toplantıda karar verip bu tabloya
ekleyin.

### Açık sorular

- [ ] **Dayanıklılık için alt süre:** "1 aydır sorunsuz" sayılsın mı? Öneri: en az 6 ay. Pilot
  yorumların çoğu yeni ürünlerden geldiği için `durability:pos` çok az kalabilir.
  - Sayım (07.11, 3.386 temiz yorum, düzenli ifadeyle kaba sayım): süre ifadesi ve "sorunsuz,
    arızasız, bozulmadı" gibi bir sözcük birlikte 112 yorumda geçiyor. Süreye göre: 1 aydan az 65
    (çoğu "2 günde geldi" gibi teslimat), 1–3 ay 13, 3–6 ay 6, 6–12 ay 3, 1 yıl ve üstü 25.
  - Sonuç: 6 ay sınırıyla bütün veride yaklaşık 28 yorum `durability:pos` olur, 400'lük havuzda
    birkaç tane. 1 ay sınırıyla yaklaşık 47.
  - Öneri: **6 ay kalsın.** Dayanıklılık uzun süreli kullanımı anlatır; birkaç haftalık "sorunsuz"
    ilk izlenimdir. Az örnek bir bulgudur ve raporda yazılır. Daha kısa süreli olumlu yorumlar
    etiketsiz kalır, `note` kolonuna "kısa süre" yazılabilir.
- [ ] **Performans aspect'i:** Yıkama ve soğutma yorumları çok sık, ama beş aspect'in dışında kalıyor.
  Hepsiburada kriterlerinde de var (Yıkama, Soğutma). Eklensin mi?
  - Sayım: yıkama, leke, sıkma, kurutma, soğutma, dondurma sözcükleri 352 yorumda (%10,4) geçiyor:
    buzdolabında 143, çamaşır makinesinde 209. Enerji (13 aday) ve servisten (18) çok daha sık.
  - Öneri: **`performance` etiketi şimdi eklensin, skora şimdilik girmesin** (enerjideki gibi).
    Etiketlemeden sonra eklemek 400 yorumu yeniden okumayı gerektirir; şimdi eklemek ucuz. Skora
    girip girmeyeceği NLP sonuçlarından sonra B3'te kararlaştırılır.
- [x] **Enerji:** Enerji kriteri yorumlardan beslenmez (karar 16). `energy` etiketi yine yazılır,
  ama skora girmez; yalnızca analiz ve raporlama içindir.

### Etiketlenecek yorumların seçimi

Rastgele seçimde enerji, arıza ve gürültü yorumları çok az çıkar. 400 yorumluk havuz iki parça olur:

- **Test (100 yorum):** Tamamen rastgele. P/R/F1 yalnızca bununla raporlanır, çünkü gerçek dağılımı
  yansıtır. Ortak 100 yorum olarak bu set kullanılır.
- **Eğitim (300 yorum):** Bilerek zenginleştirilmiş: anahtar sözcükle bulunan enerji, arıza, servis
  ve gürültü adayları ile düşük puanlı yorumlar, kalanı rastgele.

Seçim komutu: `greenchoice annotation-pool` (`src/greenchoice/nlp/pool.py`, sabit tohum 491).

- Eğitimde her nadir aspect için en fazla 40 anahtar sözcük adayı (önce enerji, sonra arıza,
  gürültü, servis), en fazla 60 düşük puanlı (3 ve altı) yorum alınır, kalan rastgele doldurulur
  ve kategoriler sırayla seçilir. Bir üründen en fazla 30 eğitim yorumu girer.
- Eğitim yorumları A ve B arasında yarı yarıya bölünür. Her etiketçi 250 yorumluk bir tablo alır:
  ortak 100 test yorumu ve kendi 150 eğitim yorumu, karışık sırada. Tabloda yorumun neden
  seçildiği, test mi eğitim mi olduğu ve yıldız puanı yoktur; etiket yalnızca metinden verilir.
- `pool.csv` yalnızca kimlikleri tutar. Tablolar yorum metni içerdiği için `data/interim/etiketleme/`
  altında kalır, repoya girmez, ikimiz arasında elden paylaşılır.
- Etiketleme başladıktan sonra havuz yeniden seçilmez; komut var olan havuzun üstüne `--force`
  olmadan yazmaz.
- 1.460 pilot yorumla deneme: anahtar sözcükle enerji 1, servis 6, arıza 14 aday bulundu, gürültü
  178. Yani zenginleştirme sınırlı kaldı, 300 eğitim yorumunun 180'i rastgele. 80 ürünün yorumları
  gelince komut yeniden çalıştırılır.

### Uyum ölçümü

- İlk 100 yorumu ikiniz ayrı ayrı etiketleyin. Aspect bazında Cohen's kappa hesaplayın.
- Kappa < 0.6 olan aspect'lerde tanımı netleştirip o 100 yorumu yeniden konuşun.

## 2. Ürün etiketleme (ground truth)

Her ürün için: **Önerilir / Nötr / Önerilmez** (`recommended / neutral / not_recommended`).

Soru: *"Fiyatı, enerji tüketimi, uzun vadeli maliyeti ve kullanıcı deneyimleri birlikte
düşünüldüğünde, bu ürünü benzer ürünler arasında bilinçli bir tercih olarak önerir miydim?"*

- Ürün sayfası, enerji etiketi bilgisi ve yorumların bir örneği birlikte değerlendirilir.
  Sistem skorunu **görmeden** etiketleyin.
- İki kişi bağımsız etiketler, sonra uyuşmazlıklar konuşulup uzlaşılmış etiket belirlenir.
- Dosya: `data/annotations/product_labels.csv` → `product_id, annotator, label, note`
