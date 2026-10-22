# Etiketleme kılavuzu (taslak)

Sorumlu: Kişi A taslak hazırlar, 07–10.11.2026 arasında birlikte kesinleştirilir.
Etiketleme başladıktan sonra kural değişirse önceki etiketler de güncellenir.

## 1. Yorum etiketleme (aspect + duygu)

Her yorum için içinde geçen **her aspect'i** ve duygusunu (`pos` / `neg`) işaretleyin.
Bir yorumda birden çok aspect olabilir. Hiçbiri yoksa yorumu boş etiketle geçin.

| Aspect | Olumlu (pos) örnek | Olumsuz (neg) örnek | Not |
|---|---|---|---|
| `durability` dayanıklılık | "3 yıldır sorunsuz", "sağlam" | "çabuk bozuldu", "kapağı kırıldı" | Ürünün uzun süre çalışıp çalışmadığı |
| `energy` enerji tüketimi | "faturam düştü", "az elektrik yakıyor" | "çok elektrik harcıyor" | Enerji sınıfının sadece tekrarlanması sayılmaz |
| `service` servis | "servis hemen geldi" | "servis gelmedi", "parça yok" | Kurulum ekibi dahil |
| `failure` arıza | — | "hata kodu verdi", "soğutmuyor" | Belirli bir arızanın bildirilmesi. Olumlu karşılığı `durability:pos` |
| `noise` gürültü | "çok sessiz" | "gürültülü", "titreşim yapıyor" | |

### Kurallar

1. **Açık ifade şartı.** Yorumcu söylemiyorsa çıkarım yapmayın. "Güzel ürün" hiçbir aspect değildir.
2. **Olumsuzlama:** "hiç bozulmadı" → `durability:pos`; "sessiz değil" → `noise:neg`.
3. **Beklenti / tahmin:** "uzun ömürlü olacağa benziyor" → etiketlemeyin (gerçek deneyim değil).
4. **Zamanla değişen deneyim:** "ilk yıl sorunsuzdu, sonra bozuldu" → son durum esas alınır:
   `durability:neg` + `failure:neg` (`durability:pos` yazılmaz).
5. **Kargo, paketleme, satıcı** ile ilgili şikâyetler etiketlenmez (ürünle ilgili değil).
6. Emin değilseniz `note` sütununa yazın, haftalık toplantıda karar verin ve buraya örnek olarak ekleyin.

### Dosya biçimi

`data/annotations/reviews_gold.csv`: `review_id, product_id, annotator, text, aspect, polarity`

```
r101,ty-1,A,"3 yıldır sorunsuz ama çok ses yapıyor",durability,pos
r101,ty-1,A,"3 yıldır sorunsuz ama çok ses yapıyor",noise,neg
r102,ty-1,A,"Kargo hızlıydı",,
```

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
