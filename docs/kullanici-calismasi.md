# Kullanıcı çalışması (A4.1 taslağı)

Sorumlu: Kişi A. Durum: **taslak** (07.11.2026). Danışmanla konuşulacak noktalar en sonda.
Ürün çiftleri skorlama kararları (B3) verildikten sonra son skorlarla seçilecek.

## Amaç

Proje önerisindeki değerlendirme ölçütü: "üretilen açıklamaların kullanıcı tarafından
anlaşılabilirliği". Çalışma iki soruya cevap arar:

1. **Anlaşılabilirlik:** Açıklamalar, kullanıcının skorun neden o değerde olduğunu doğru
   anlamasını sağlıyor mu?
2. **Güven ve karar:** Açıklama gösterildiğinde kullanıcı skora daha çok (veya daha yerinde) güveniyor
   mu, kararından daha emin oluyor mu?

Çalışma küçük ölçeklidir (10–15 kişi). Sonuçlar keşif niteliğindedir; genelleme iddiası taşımaz.

## Tasarım

- **Katılımcı içi (within-subjects):** Her katılımcı iki koşulu da görür.
  - **Koşul S (skor):** Ürün kartında yalnızca GreenChoice skoru ve etiketi.
  - **Koşul A (açıklamalı):** Skor, etiket, kriter kırılımı ve metin açıklamaları
    (ör. "12 yıllık toplam kullanım maliyeti benzer ürünlerden düşük").
- Her koşulda 3 görev, toplam 6 görev. Her görev bir kategoride iki ürün arasında seçimdir.
- **Sıra dengelemesi:** Katılımcıların yarısı önce S sonra A, diğer yarısı tersi. Ürün çiftleri iki
  set halinde (Set 1, Set 2) hazırlanır ve setlerin koşullara atanması da dengelenir:

| Grup | Önce | Sonra |
|---|---|---|
| 1 | S + Set 1 | A + Set 2 |
| 2 | S + Set 2 | A + Set 1 |
| 3 | A + Set 1 | S + Set 2 |
| 4 | A + Set 2 | S + Set 1 |

Katılımcılar sırayla gruplara atanır (1, 2, 3, 4, 1, …).

## Ürün çiftleri

Gerçek veriden, aynı kategoriden 12 çift (6 + 6; iki set, her sette 3 buzdolabı ve 3 çamaşır makinesi
çifti olacak şekilde), şu kurallarla:

- Skor farkı 3–10 puan: seçim apaçık olmasın.
- Çiftteki iki ürünü ayıran ana kriter farklı olsun (ör. birinde düşük fiyat, diğerinde düşük
  toplam maliyet), böylece açıklama gerçekten bilgi taşır.
- Fiyatı daha yüksek olan ürün en az birkaç çiftte daha yüksek skorlu olsun (fiyat tek ipucu kalmasın).
- Enerji verisi eksik (medyanla doldurulmuş) ürün çiftlere alınmaz; açıklama eksik kalır.
- Marka adları gösterilir (gerçekçilik için), ama aynı marka bir çiftte iki kez yer almaz.

Seçim kodla yapılıp liste `data/interim/kullanici_calismasi/ciftler.csv` dosyasına yazılabilir
(henüz yazılmadı).

## Akış (katılımcı başına yaklaşık 20 dakika)

1. Bilgilendirme ve onam (aşağıda), 2 dakika.
2. Ön sorular (aşağıda), 1 dakika.
3. Kısa tanıtım: "GreenChoice ürünleri enerji, uzun vadeli maliyet, dayanıklılık ve kullanıcı
   yorumlarına göre puanlar." Örnek bir ürün kartı gösterilir, 2 dakika.
4. Birinci koşul: 3 görev, her görevden sonra görev soruları, ~6 dakika.
5. Birinci koşul sonu soruları, 1 dakika.
6. İkinci koşul: 3 görev ve sorular, ~6 dakika.
7. İkinci koşul sonu soruları ve karşılaştırma soruları, 2 dakika.

Oturumlar yüz yüze veya ekran paylaşımıyla yapılır; araştırmacı yönlendirme yapmaz, yalnızca
arayüzle ilgili teknik soruları cevaplar.

## Ölçümler

### Her görevden sonra

1. Hangi ürünü seçerdiniz? (Ürün X / Ürün Y)
2. Kararınızdan ne kadar eminsiniz? (1 Hiç emin değilim – 5 Çok eminim)
3. **Anlama sorusu (nesnel):** "Ürün X'in skorunun Ürün Y'den yüksek olmasının ana nedeni sizce
   nedir?" Dört seçenek, biri doğru (sistemin en büyük katkılı kriteri), biri "Bilmiyorum".
   Koşul S'de de sorulur; burada doğru cevap oranı tahmin düzeyine yakın olmalı.

### Her koşulun sonunda (1 Kesinlikle katılmıyorum – 5 Kesinlikle katılıyorum)

Maddeler bu çalışma için yazılmıştır. Kavramlar, açıklama memnuniyeti (Hoffman ve diğ., 2018) ve
otomasyona güven (Jian ve diğ., 2000) çalışmalarındaki boyutlardan esinlenir; bu maddeler o
ölçeklerin kendisi veya geçerlenmiş çevirisi **değildir**.

| Kod | Madde | Boyut |
|---|---|---|
| K1 | Skorun nasıl oluştuğunu anladım. | Anlaşılabilirlik |
| K2 | Bir ürünün neden daha yüksek puan aldığını kendi cümlelerimle anlatabilirim. | Anlaşılabilirlik |
| K3 | Gösterilen bilgiler karar vermem için yeterliydi. | Yeterlilik |
| K4 | Gösterilen bilgiler karar vermemi kolaylaştırdı. | Fayda |
| K5 | Sistemin puanlarına güvenirim. | Güven |
| K6 | Sistemin puanı kendi değerlendirmemle çelişseydi, puanı sorgulardım. *(ters değil; yerinde güven)* | Yerinde güven |
| K7 | Bu sistemi gerçek bir alışverişte kullanmak isterim. | Kullanım niyeti |

### Sonda (yalnızca bir kez)

- "Hangi gösterimi tercih edersiniz?" (Yalnızca skor / Skor ve açıklama / Fark etmez)
- Açık uçlu: "Açıklamalarda anlaşılmayan veya eksik bulduğunuz bir şey oldu mu?"
- Açık uçlu: "Bir ürünü seçerken en çok neye baktınız?"

### Ön sorular (kişisel veri toplanmaz)

- Yaş aralığı (18–24 / 25–34 / 35–49 / 50+)
- Son 3 yılda beyaz eşya aldınız mı veya alımına katıldınız mı? (Evet / Hayır)
- Alışverişte enerji sınıfına ne kadar dikkat edersiniz? (1–5)

İsim, e-posta, okul numarası **sorulmaz**. Katılımcılar K01, K02, … diye numaralanır.

## Kayıt

Sonuçlar tek bir tabloya yazılır: `data/interim/kullanici_calismasi/sonuclar.csv` (repoya girmez).
Kolonlar: `katilimci, grup, kosul, sira, gorev, cift_id, secim, eminlik, anlama_cevap,
anlama_dogru, K1 … K7, tercih, acik_1, acik_2, yas_araligi, beyaz_esya, enerji_dikkat`.
Açık uçlu cevaplarda kişiyi tanıtan bir şey varsa analizden önce silinir.

## Analiz planı (A4.3)

- **Ana karşılaştırma:** Katılımcı başına koşul ortalamaları; S ve A arasında **Wilcoxon işaretli
  sıralar testi** (eşleştirilmiş, sıralı veri, küçük örneklem). Medyan, çeyrekler arası aralık ve etki
  büyüklüğü (r) raporlanır. Yedi madde için ayrı test yapıldığından p değerleri Holm düzeltmesiyle
  verilir.
- **Anlama:** Doğru cevap oranı S ve A'da (katılımcı başına 3 sorudan); aynı test.
- **Sıra etkisi:** Önce S görenlerle önce A görenler ayrı ayrı da gösterilir; n küçük olduğu için test
  edilmez, yalnızca tabloda verilir.
- **Açık uçlu cevaplar:** Kısa tema listesi (ör. "maliyet hesabı anlaşılmadı", "yorum sayısı merak
  edildi"); açıklama metinlerini iyileştirmek için kullanılır.
- 10–15 kişiyle küçük farklar istatistiksel olarak görünmeyebilir; anlamlı çıkmayan sonuç "fark yok"
  diye yorumlanmaz.

## Bilgilendirme ve onam metni (taslak)

> Bu çalışma, [üniversite adı] COMP 491 bitirme projesi kapsamında geliştirilen GreenChoice ürün
> değerlendirme prototipinin anlaşılabilirliğini ölçmek için yapılmaktadır. Yaklaşık 20 dakika
> sürecek; ekranda gösterilen ürünler arasında seçim yapıp kısa sorular cevaplayacaksınız. Doğru veya
> yanlış cevap yoktur; değerlendirilen siz değil, sistemdir. Adınız veya iletişim bilginiz
> kaydedilmez, cevaplarınız yalnızca toplu olarak raporlanır. Katılım gönüllüdür; istediğiniz anda
> gerekçe göstermeden bırakabilirsiniz. Sorularınız için: Atahan Bulut, Ali Rubar Kal (proje
> ekibi), danışman: Tuna Çakar.
>
> Devam ederek katılmayı kabul ediyorum. ☐

> Not: [üniversite adı] yerine kurumun resmî adı yazılacak.

## Hazırlık listesi

- [ ] Skorlama kararları (B3) ve son skorlar
- [ ] Ürün çiftlerinin seçimi (kodla, yukarıdaki kurallarla)
- [ ] Arayüzde iki gösterim: skor-yalnız ve açıklamalı (B4.1 ile birlikte; bir URL parametresi yeterli)
- [ ] Anket formu (Google Forms veya kâğıt) ve sonuç tablosu
- [ ] 2 kişilik pilot oturum, süre ve anlaşılmayan soruların düzeltilmesi
- [ ] Katılımcı bulma (10–15 kişi; ekip üyeleri katılmaz)

## Danışmana sorulacaklar

1. Bu ölçekte (anonim, 15 kişiden az, düşük riskli) bir kullanıcı çalışması için etik kurul onayı
   gerekiyor mu? Gerekiyorsa başvuru süresi takvime sığar mı (çalışma Ocak ortasında)?
2. Katılımcı içi tasarım ve Wilcoxon testi yeterli mi, yoksa yalnızca betimsel sonuç mu bekleniyor?
3. Katılımcılar öğrenci olabilir mi, yoksa beyaz eşya alan farklı yaş gruplarından mı olmalı?

## Kaynaklar

- Hoffman, R. R., Mueller, S. T., Klein, G., Litman, J. (2018). Metrics for Explainable AI:
  Challenges and Prospects. arXiv:1812.04608. https://arxiv.org/abs/1812.04608
- Jian, J.-Y., Bisantz, A. M., Drury, C. G. (2000). Foundations for an Empirically Determined Scale of
  Trust in Automated Systems. International Journal of Cognitive Ergonomics, 4(1), 53–71.
