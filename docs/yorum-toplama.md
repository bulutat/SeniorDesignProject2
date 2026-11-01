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
