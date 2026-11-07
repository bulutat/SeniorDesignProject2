# Literatür

Her kaynak için künye ve 2–3 cümlelik özet. Künyeler kaynak sayfasından kontrol edildi
(07.11.2026). Tam metni okunmayan kaynaklarda bu açıkça yazılır; rapora girmeden önce tam metin
okunmalı.

## NLP (Kişi A, görev A0.2)

### Temel yöntem

1. **Devlin, J., Chang, M.-W., Lee, K., Toutanova, K. (2019). BERT: Pre-training of Deep
   Bidirectional Transformers for Language Understanding.** NAACL-HLT 2019, s. 4171–4186.
   https://aclanthology.org/N19-1423/
   Maskeli dil modeliyle önceden eğitilen, sonra göreve göre ince ayar (fine-tune) yapılan
   çift yönlü Transformer kodlayıcı. Sınıflandırma için `[CLS]` temsilinin üstüne tek bir katman
   eklenir. Projedeki BERTurk yaklaşımının dayandığı model.

2. **Schweter, S. (2020). BERTurk – BERT models for Turkish (v1.0.0).** Zenodo.
   https://doi.org/10.5281/zenodo.3770924
   Türkçe için eğitilmiş BERT modelleri: büyük/küçük harf duyarlı ve duyarsız, 32k ve 128k
   sözlüklü sürümler; model kartına göre 35 GB metinle eğitildi. Kullandığımız model
   `dbmdz/bert-base-turkish-cased` (32k, büyük/küçük harf duyarlı).

### Aspect tabanlı duygu analizi (ABSA)

3. **Pontiki, M., Galanis, D., Pavlopoulos, J., Papageorgiou, H., Androutsopoulos, I.,
   Manandhar, S. (2014). SemEval-2014 Task 4: Aspect Based Sentiment Analysis.** SemEval 2014,
   s. 27–35. https://aclanthology.org/S14-2004/
   ABSA'yı ortak görev olarak tanımlayan çalışma: bir yorumdaki aspect'leri bulmak ve her biri
   için duyguyu belirlemek. Dizüstü bilgisayar ve restoran yorumları, dört alt görev (aspect
   terimi, aspect kategorisi ve her biri için duygu). Bizim görevimiz "aspect kategorisi + duygu"
   alt görevine karşılık geliyor; aspect listemiz sabit (dayanıklılık, enerji, servis, arıza, gürültü).

4. **Sun, C., Huang, L., Qiu, X. (2019). Utilizing BERT for Aspect-Based Sentiment Analysis via
   Constructing Auxiliary Sentence.** NAACL-HLT 2019, s. 380–385.
   https://doi.org/10.18653/v1/N19-1035
   Her aspect için yardımcı bir cümle kurup ("servis hakkında ne düşünülüyor?") ABSA'yı cümle
   çifti sınıflandırmasına çeviriyor; SemEval-2014 ve SentiHood'da o dönemin en iyi sonuçları.
   Bizim için alternatif kurulum: tek model ve 9 sigmoid çıkış yerine aspect başına bir soru.
   Veri azsa karşılaştırmaya değer.

### Türkçe çalışmalar

5. **Yaman, S., Aslan, Ö. Multi-Aspect Sentiment Analysis on Turkish Food Delivery Reviews: A
   Multi-Task BERTurk Approach.** International Journal of Innovative Engineering Applications
   (ISSN 2587-1943). https://doi.org/10.46460/ijiea.1956584
   Yemek Sepeti'nin 676.214 yorumunda hız, servis ve lezzet puanlarını BERTurk ile tahmin ediyor;
   ortak kodlayıcılı çok görevli model ve sınıf ağırlıklı kayıp en iyi sonucu veriyor. Hata
   analizinde metinle puanın çeliştiği yorumlar ve "orta" sınıfın zorluğu öne çıkıyor; bizim
   verimizde de yorumların %87'si 5 yıldızlı. Bilinen tek Türkçe çok-aspect'li BERTurk çalışması
   olarak en yakın örnek; ancak etiketler kullanıcı puanlarından geliyor, elle etiketleme yok.
   **Yayın yılı ve cilt doğrulanmadı** (yalnızca özet okundu).

6. **Güven, Z. A. (2021). The Effect of BERT, ELECTRA and ALBERT Language Models on Sentiment
   Analysis for Turkish Product Reviews.** 6th International Conference on Computer Science and
   Engineering (UBMK), IEEE, s. 629–632. https://doi.org/10.1109/UBMK52708.2021.9559007
   Hepsiburada ürün yorumlarında belge düzeyinde (aspect'siz) duygu analizi. Klasik yöntemlerden
   en iyisi Naive Bayes (%89,95), dil modellerinden ELECTRA (%92,54). Bizimle aynı site ve
   alan, ama aspect düzeyinde değil; Türkçe ürün yorumunda transformer'ların klasik yöntemleri
   geçtiğini gösteren yerel bir örnek.

7. **Bilgin, M., Turan, M. (2025). Aspect-Based Sentiment Analysis for Turkish Reviews Using
   Token and Sequential Classification Methods.** International Journal of Computer and
   Information Technology, 14(3), s. 90–99. https://doi.org/10.24203/2drscx54
   Türkçe yorumlarda aspect terimi çıkarma ve duygu sınıflandırmasını token sınıflandırması ve
   dizi sınıflandırması olarak ele alıyor, birden fazla transformer'ı karşılaştırıyor.
   **Yalnızca künye doğrulandı**; veri seti, modeller ve sonuçlar tam metinden okunmalı.

### Etiketleme ve değerlendirme

8. **Cohen, J. (1960). A Coefficient of Agreement for Nominal Scales.** Educational and
   Psychological Measurement, 20(1), s. 37–46. https://doi.org/10.1177/001316446002000104
   İki etiketçinin şans eseri uyumunu düşerek uyumu ölçen kappa katsayısı. Ortak 100 yorumda
   aspect bazında hesaplanacak (O2.1).

### Projeye çıkarımlar

- **Görev tanımı:** Sabit aspect listesiyle "aspect kategorisi + duygu" (kaynak 3). Bir yorumda
  birden fazla etiket olabildiği için 9 etiketli çok etiketli sınıflandırma, sigmoid çıkış ve
  BCE kaybı. Alternatif olarak yardımcı cümle kurulumu (kaynak 4).
- **Sınıf dengesizliği:** Enerji ve servis yorumları çok az (havuzda 13 ve 17 aday). Kaynak 5'teki
  sınıf ağırlıklı kayıp ve etiket başına eşik ayarı (doğrulama setinde) denenmeli.
- **Az veri:** Bizde yaklaşık 300 eğitim yorumu olacak; kaynak 5 ve 6'daki veri miktarının çok
  altında. Sonuçlar kural tabanlı yöntem ve TF-IDF ile aynı test setinde karşılaştırılmalı; BERTurk'ün
  daha iyi olacağı varsayılmamalı.
- **Puan ≠ metin:** Kaynak 5, metinle puanın çeliştiği yorumları bildiriyor. Etiketlemeyi yalnızca
  metinden yapmamızın (tablolarda yıldız puanı yok) bir gerekçesi.
- **Boşluk:** Türkçe beyaz eşya yorumlarında aspect düzeyinde, elle etiketlenmiş bir çalışma
  bulunamadı. Bu, projenin katkısı olarak yazılabilir; ancak arama kapsamlı değildi
  (07.11.2026, genel web araması), rapordan önce Google Scholar ve DergiPark'ta tekrar bakılmalı.

### Colab denemesi

Defter: `notebooks/02_A_berturk_denemesi.ipynb` (uydurma cümlelerle; tokenizer, `[CLS]` temsili,
9 etiketli sınıflandırma başı ve 30 adımlık deneme eğitimi).

- [ ] Colab'da çalıştırıldı mı, GPU türü, süreler: _henüz çalıştırılmadı_
