# Yorum toplama kılavuzu (kaydedilen sayfalar)

Siteler otomatik yorum toplamaya izin vermediği için (`kaynak-inceleme.md`) yorum sayfaları
**elle, normal tarayıcıdan** kaydedilir. `greenchoice import-reviews` yalnızca bu dosyaları okur,
internete bağlanmaz ve kullanıcı adlarını almaz.

Toplanan dosyalar ve `reviews.csv` repoya girmez, proje dışında paylaşılmaz.

## Trendyol

1. Ürün adresinin sonuna `/yorumlar` ekleyip sayfayı aç.
2. Yeni yorum gelmeyene kadar en alta kaydır.
3. Kesik yorumları aç: `F12` → **Console**, aşağıdaki satırı yapıştır, Enter:

   ```js
   document.querySelectorAll('button.read-more').forEach(b => b.click())
   ```

   Tarayıcı yapıştırmaya izin vermezse yazdığı onay ifadesini bir kez yaz.
4. `Ctrl+S` → **Web Sayfası, Tamamı** → `data/raw/yorum_sayfalari/`.

## Hepsiburada

Sayfa başına 10 yorum var. Sayfa altındaki numaralarla her sayfaya geç ve her birini ayrı kaydet.

1. Ürün adresinin sonuna `-yorumlari` ekleyip sayfayı aç.
2. `Ctrl+S` → **Web Sayfası, Tamamı** → `data/raw/yorum_sayfalari/`.
3. Dosya adı aynı olmasın diye sonuna `syf 2`, `syf 3` ekle.

## Dönüştürme

```bash
greenchoice import-reviews
```

Varsayılan girdiler `data/raw/yorum_sayfalari/` ve `data/interim/pilot_products.csv`, çıktı
`data/interim/reviews.csv`. Komut her çalıştırmada klasörün tamamını yeniden okur, aynı yorum iki
kez kaydedildiyse tek sayılır.

Rapordaki alanlar:

| Alan | Anlamı | Ne yapılır |
|---|---|---|
| `reviews` | Metni olan yorum sayısı | |
| `missing` | Trendyol: sitenin bildirdiği yorumlardan eksik kalan | 0 değilse sayfayı sonuna kadar kaydırıp yeniden kaydet |
| `truncated` | "Devamını Oku" açılmadan kaydedilen yorum | 0 değilse 3. adımı yapıp yeniden kaydet |
| `missing_pages` | Hepsiburada: kaydedilmemiş sayfa numaraları | Eksik sayfaları kaydet |
| `without_text` | Metni olmayan değerlendirme | Bir şey gerekmez, yorum tablosuna girmez |

Bir sayfayı yeniden kaydederken eski dosyanın üzerine yaz veya eskisini sil. İkisi birden
klasörde kalırsa kesik sürüm tam sürümün yerine geçebilir.

Bir dosya okunamazsa komut dosya adıyla durur. Site tasarımı değiştiyse seçicilerin
`collect/saved_pages.py` içinde güncellenmesi gerekir.

## Ek veri: Hepsiburada kriter puanları

Bazı yorumlarda kullanıcılar "Enerji Tüketimi", "Sessiz Çalışma" gibi kriterlere ayrıca puan veriyor.
Bunlar `site_aspects` kolonuna JSON olarak yazılır. Kriter adları kategoriye göre değişebilir.

## Temizleme (A1.2)

`clean_reviews` ham metni değiştirmez, `text_clean` ve `text_product` kolonlarını ekler.

- **Uzatılmış harf ve emoji:** "çoook" → "çok", emojiler silinir. Üç aynı harf tek harfe iner, bu
  yüzden nadiren "etttim" → "etim" gibi bozulma olur.
- **Dil filtresi yok:** Pilot yorumlarda Türkçe dışı yorum görülmedi. Şüpheli görünenlerin baktığımız
  örnekleri Türkçe karaktersiz yazılmış Türkçeydi ("cok memnunum").
- **Teslimat bağlamı:** "sorunsuz" ve "sağlam" yanındaki 4 kelime içinde teslimat veya kurulum
  sözcüğü varsa `text_product`'tan çıkar. Hemen ardından "çalışıyor/kullanıyorum" geliyorsa kalır.

Pilot yorumlarda kural tabanlı `durability:pos` sayısı (1.460 yorum, 01.11.2026):

| Yöntem | durability:pos | Diğer aspect'ler |
|---|---|---|
| Temizleme yok | 218 | |
| Tümce parçası silme (denendi, bırakıldı) | 63 | Sessizlik 183 → 159 düştü, 256 yorum tamamen elendi |
| Yalnızca belirsiz sözcüğü çıkarma (seçildi) | 41 | Değişmedi |

Tümce silme bırakıldı, çünkü noktalama az olduğunda ürün bilgisi de siliniyordu. Kalan 41 sonucun
rastgele 30'luk örneğini elle okuduk: yaklaşık üçte ikisi gerçekten dayanıklılık, kalanı hatalı
("sağlamak", satıcı adı "Dayanıklı Tüketim"). Bu resmî bir ölçüm değildir, gerçek başarı etiketli
veriyle ölçülecek (P/R/F1).

Bilinen sınırlar: kargo veya satıcı şikâyeti içeren yorumlar silinmez ve yıldız puanına etkisi
düzeltilmez. Aspect sözlüğü Türkçe karaktersiz yazımı ("sorunsuz" dışında "cok", "calisiyor")
yakalamaz.
