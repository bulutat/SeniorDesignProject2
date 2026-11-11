# Literatür

Okuma notları (Türkçe). Raporun 3.1 bölümü (Literature Survey) İngilizce ve **kendi cümlelerinizle**
yazılır; bu notlar rapora kopyalanmaz. Hoca en az 12 bilimsel çalışmanın ayrıntılı incelenmesini,
uygun formatta atıf yapılmasını ve makalelerin Drive linkiyle paylaşılmasını istiyor.

- Künyeler yayıncı veya arşiv sayfasından kontrol edildi (07.11 ve 10.11.2026).
- Her kaynakta **"Okunan"** satırı, notun neye dayandığını söyler: tam metin, özet veya yalnızca künye.
  Yalnızca özeti okunan kaynaklar raporda ayrıntılı özetlenmeden önce tam metinden okunmalı.
- **PDF** satırı açık erişimli kopyanın yerini verir; "kütüphane" yazanlar için üniversite erişimi
  gerekir. İndirip Drive klasörüne koyun.

Toplam 20 kaynak: 19 bilimsel çalışma + 1 yazılım sürümü (BERTurk).

## 1. Yorumlardan görüş ve aspect çıkarımı

**[1] Hu, M., Liu, B. (2004). Mining and summarizing customer reviews.** Proceedings of the 10th
ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '04), s. 168–177.
https://doi.org/10.1145/1014052.1014073
- Okunan: özet ve ikincil özetler. PDF: kütüphane (ACM).
- Amaç: Bir ürünün çok sayıdaki yorumunu, özellik bazında olumlu/olumsuz görüş özeti hâline getirmek.
- Yöntem: Üç adım: yorumlarda sık geçen ürün özelliklerini (ad öbekleri) bulmak, görüş cümlelerini
  bulup sıfat sözlüğüyle olumlu/olumsuz belirlemek, sonuçları özellik bazında özetlemek.
- Önemi: Aspect tabanlı duygu analizi araştırma alanını başlatan çalışmalardan sayılır.
- Projeyle ilişkisi: Kural tabanlı yöntemimizin (sözlük + anahtar ifade) düşünsel atası. Fark:
  biz özellikleri (aspect) yorumdan keşfetmiyoruz, beş aspect'i baştan sabitliyoruz.

**[2] Pontiki, M., Galanis, D., Pavlopoulos, J., Papageorgiou, H., Androutsopoulos, I., Manandhar, S.
(2014). SemEval-2014 Task 4: Aspect Based Sentiment Analysis.** Proceedings of SemEval 2014,
s. 27–35. https://aclanthology.org/S14-2004/
- Okunan: özet. PDF: açık (ACL Anthology).
- ABSA'yı ortak görev olarak tanımlıyor: bir yorumdaki aspect'leri bulmak ve her biri için duyguyu
  belirlemek. Dizüstü bilgisayar ve restoran yorumları; dört alt görev (aspect terimi, aspect
  kategorisi ve her biri için duygu).
- Projeyle ilişkisi: Bizim görevimiz "aspect kategorisi + duygu" alt görevine karşılık geliyor.

**[3] Pontiki, M., Galanis, D., Papageorgiou, H., Androutsopoulos, I., Manandhar, S., AL-Smadi, M.,
et al. (2016). SemEval-2016 Task 5: Aspect Based Sentiment Analysis.** Proceedings of SemEval-2016,
s. 19–30. https://doi.org/10.18653/v1/S16-1002
- Okunan: tam metnin ilgili bölümleri (görev tanımı, veri setleri). PDF: açık (ACL Anthology).
- Görevin üçüncü yılı: 8 dil ve 7 alanda 19 eğitim ve 20 test veri seti, cümle ve metin düzeyinde
  ABSA, 29 takımdan 245 gönderim. Türkçe dahil: restoran ve telekom veri setleri, iki dilbilimci
  tarafından etiketlenmiş, bir düzenleyici tarafından kontrol edilmiş.
- Alt görevler: aspect kategorisi (varlık–özellik çifti), görüş hedefi ve duygu (slot 1–3).
- Projeyle ilişkisi: Türkçe ABSA için bilinen bir ortak veri seti var, ama beyaz eşya yok. Etiketleme
  sürecimiz (iki etiketçi + uzlaşma) bu çalışmanın yaklaşımına benziyor. Bizdeki metin düzeyi
  etiketleme (yorum başına aspect:duygu) onların metin düzeyi alt görevine karşılık geliyor.

## 2. Transformer modelleri ve Türkçe

**[4] Devlin, J., Chang, M.-W., Lee, K., Toutanova, K. (2019). BERT: Pre-training of Deep
Bidirectional Transformers for Language Understanding.** NAACL-HLT 2019, s. 4171–4186.
https://aclanthology.org/N19-1423/
- Okunan: özet ve yöntem bölümü. PDF: açık (ACL Anthology, arXiv 1810.04805).
- Maskeli dil modeli ve sonraki cümle tahminiyle önceden eğitilen çift yönlü Transformer kodlayıcı;
  göreve göre ince ayar (fine-tune) yapılıyor. Sınıflandırmada `[CLS]` temsili üstüne tek bir katman.
- Projeyle ilişkisi: BERTurk yaklaşımımızın dayandığı model; çok etiketli sınıflandırma başı bu
  yapının üstüne ekleniyor.

**[5] Schweter, S. (2020). BERTurk – BERT models for Turkish (v1.0.0).** Zenodo (yazılım).
https://doi.org/10.5281/zenodo.3770924
- Okunan: Zenodo kaydı ve model kartı. Bilimsel makale değil, 12'lik sayıya katılmamalı.
- Türkçe BERT modelleri: büyük/küçük harf duyarlı ve duyarsız, 32k ve 128k sözlüklü sürümler; model
  kartına göre 35 GB metinle eğitildi. Kullandığımız: `dbmdz/bert-base-turkish-cased`.

**[6] Sun, C., Huang, L., Qiu, X. (2019). Utilizing BERT for Aspect-Based Sentiment Analysis via
Constructing Auxiliary Sentence.** NAACL-HLT 2019, s. 380–385. https://doi.org/10.18653/v1/N19-1035
- Okunan: özet. PDF: açık (ACL Anthology).
- Her aspect için yardımcı bir cümle kurup ("servis hakkında ne düşünülüyor?") ABSA'yı cümle çifti
  sınıflandırmasına çeviriyor; SemEval-2014 ve SentiHood'da o dönemin en iyi sonuçları.
- Projeyle ilişkisi: 9 sigmoid çıkışlı tek model yerine alternatif kurulum; veri az olduğunda
  karşılaştırmaya değer.

**[7] Yaman, S., Aslan, Ö. Multi-Aspect Sentiment Analysis on Turkish Food Delivery Reviews: A
Multi-Task BERTurk Approach.** International Journal of Innovative Engineering Applications
(ISSN 2587-1943). https://doi.org/10.46460/ijiea.1956584
- Okunan: özet. Yayın yılı ve cilt doğrulanmadı. PDF: DergiPark (açık olması beklenir, kontrol edin).
- Yemek Sepeti'nin 676.214 yorumunda hız, servis ve lezzet puanlarını BERTurk ile tahmin ediyor;
  ortak kodlayıcılı çok görevli model ve sınıf ağırlıklı kayıp en iyi sonucu veriyor. Hata
  analizinde metinle puanın çeliştiği yorumlar ve "orta" sınıfın zorluğu öne çıkıyor.
- Projeyle ilişkisi: En yakın Türkçe çok-aspect'li BERTurk örneği; etiketler kullanıcı puanından
  geliyor, elle etiketleme yok. Sınıf ağırlıklı kaybı BERTurk eğitim defterimizde kullandık.

**[8] Güven, Z. A. (2021). The Effect of BERT, ELECTRA and ALBERT Language Models on Sentiment
Analysis for Turkish Product Reviews.** 6th International Conference on Computer Science and
Engineering (UBMK), IEEE, s. 629–632. https://doi.org/10.1109/UBMK52708.2021.9559007
- Okunan: özet. PDF: kütüphane (IEEE).
- Hepsiburada ürün yorumlarında belge düzeyinde duygu analizi. Klasik yöntemlerden en iyisi
  Naive Bayes (%89,95), dil modellerinden ELECTRA (%92,54).
- Projeyle ilişkisi: Aynı site ve alan, ama aspect düzeyinde değil.

**[9] Bilgin, M., Turan, M. (2025). Aspect-Based Sentiment Analysis for Turkish Reviews Using Token
and Sequential Classification Methods.** International Journal of Computer and Information
Technology, 14(3), s. 90–99. https://doi.org/10.24203/2drscx54
- Okunan: **yalnızca künye**. Veri seti, modeller ve sonuçlar tam metinden okunmalı.
- Konu: Türkçe yorumlarda aspect terimi çıkarma ve duygu sınıflandırması, birden fazla transformer.

## 3. Açıklanabilirlik

**[10] Ribeiro, M. T., Singh, S., Guestrin, C. (2016). "Why Should I Trust You?": Explaining the
Predictions of Any Classifier.** Proceedings of the 22nd ACM SIGKDD (KDD '16), s. 1135–1144.
https://doi.org/10.1145/2939672.2939778
- Okunan: özet. PDF: açık (arXiv 1602.04938).
- LIME: herhangi bir modelin tek bir tahminini, o tahmin çevresinde örnekleme yapıp basit (doğrusal)
  bir modelle yaklaşarak açıklıyor. Kullanıcıların modele güvenip güvenmeyeceğine karar vermesine
  yardım ettiğini kullanıcı deneyleriyle gösteriyor.
- Projeyle ilişkisi: ML skorlayıcının (B3.2) tek tek ürün kararlarını açıklamak için SHAP'a alternatif.

**[11] Lundberg, S. M., Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions.**
Advances in Neural Information Processing Systems 30 (NIPS 2017), s. 4765–4774.
https://papers.nips.cc/paper/7062-a
- Okunan: özet. PDF: açık (NeurIPS, arXiv 1705.07874).
- SHAP: oyun teorisindeki Shapley değerlerine dayanan, her özelliğin bir tahmine katkısını veren
  birleşik çerçeve; LIME gibi yöntemleri özel durum olarak kapsıyor ve istenen özellikleri (yerel
  doğruluk, tutarlılık) sağlayan tek çözüm olduğunu savunuyor.
- Projeyle ilişkisi: Proje önerisindeki açıklanabilirlik bileşeni. Ağırlıklı skorda katkılar zaten
  doğrudan hesaplanıyor (ağırlık × kriter farkı); ML skorlayıcıda SHAP kullanılacak.

**[12] Zhang, Y., Chen, X. (2020). Explainable Recommendation: A Survey and New Perspectives.**
Foundations and Trends in Information Retrieval, 14(1), s. 1–101. https://doi.org/10.1561/1500000066
- Okunan: özet. PDF: açık (arXiv 1804.11192).
- Açıklamalı öneri sistemleri üzerine kapsamlı derleme: açıklamanın bilgi kaynağı / gösterim biçimi
  (ör. metin cümlesi, özellik, yorum) ve üretim yöntemi olmak üzere iki boyutlu sınıflandırma.
- Projeyle ilişkisi: Açıklama türümüz "özellik tabanlı metin açıklaması" (ör. "toplam maliyeti
  benzer ürünlerden düşük"); bu sınıflandırmada nerede durduğumuzu raporda göstermek için.

**[13] Hoffman, R. R., Mueller, S. T., Klein, G., Litman, J. (2018). Metrics for Explainable AI:
Challenges and Prospects.** arXiv:1812.04608. https://arxiv.org/abs/1812.04608
- Okunan: özet. PDF: açık (arXiv). Genişletilmiş dergi sürümü: Frontiers in Computer Science (2023),
  https://doi.org/10.3389/fcomp.2023.1096257.
- Açıklamaların değerlendirilmesini altı alanda ele alıyor: açıklama kalitesi (araştırmacı
  değerlendirmesi), kullanıcı memnuniyeti, kullanıcının anlaması, merak, yerinde güven, insan–sistem
  performansı. Açıklama memnuniyeti ölçeği öneriyor.
- Projeyle ilişkisi: Kullanıcı çalışması tasarımımızın (A4.1) kavramsal dayanağı.

**[14] Jian, J.-Y., Bisantz, A. M., Drury, C. G. (2000). Foundations for an Empirically Determined
Scale of Trust in Automated Systems.** International Journal of Cognitive Ergonomics, 4(1), s. 53–71.
- Okunan: özet ve ikincil kaynaklar. PDF: kütüphane (DTIC'te teknik rapor sürümü var).
- Otomasyona güveni kuramdan değil veriden türeten çalışma: katılımcıların güven/güvensizlik
  sözcüklerini derecelendirmesiyle 12 maddelik ölçek. Sonraki çalışmalar ölçeğin olumlu yanlılığını
  ve faktör yapısını tartışıyor.
- Projeyle ilişkisi: Kullanıcı çalışmasındaki güven maddelerinin kavramsal kaynağı.

## 4. Çok kriterli karar ve skor modeli

**[15] Saaty, T. L. (1990). How to make a decision: The analytic hierarchy process.** European
Journal of Operational Research, 48(1), s. 9–26. https://doi.org/10.1016/0377-2217(90)90057-I
- Okunan: özet. PDF: kütüphane (Elsevier).
- AHP'ye giriş: kriterleri hiyerarşiye koymak, ikili karşılaştırmalarla (1–9 ölçeği) göreli önem
  vermek, ağırlıkları özvektörden bulmak ve tutarlılığı kontrol etmek.
- Projeyle ilişkisi: Kriter ağırlıklarını gerekçelendirmek için kullandığımız yöntem (`scoring/ahp.py`,
  tutarlılık oranı < 0,1).

**[16] Chen, T., Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System.** Proceedings of the
22nd ACM SIGKDD (KDD '16), s. 785–794. https://doi.org/10.1145/2939672.2939785
- Okunan: özet. PDF: açık (arXiv 1603.02754).
- Seyrek veriye duyarlı algoritma, yaklaşık öğrenme için ağırlıklı quantile sketch ve önbellek,
  sıkıştırma, parçalama optimizasyonlarıyla ölçeklenebilir gradyan artırmalı ağaç sistemi.
- Projeyle ilişkisi: Proje önerisinde karşılaştırılacak ML modellerinden biri (B3.2). Bizdeki veri
  çok küçük (80 ürün); bu yüzden basit modellerin (LR) de karşılaştırmada olması önemli.

**[17] Cohen, J. (1960). A Coefficient of Agreement for Nominal Scales.** Educational and
Psychological Measurement, 20(1), s. 37–46. https://doi.org/10.1177/001316446002000104
- Okunan: künye ve ikincil kaynaklar. PDF: kütüphane (SAGE).
- İki etiketçinin şans eseri uyumunu düşerek uyumu ölçen kappa katsayısı.
- Projeyle ilişkisi: Ortak 100 yorumda aspect bazında etiketçi uyumu (`collect-labels`).

## 5. Enerji verimliliği ve tüketici kararı

**[18] Allcott, H., Greenstone, M. (2012). Is There an Energy Efficiency Gap?** Journal of Economic
Perspectives, 26(1), s. 3–28. https://doi.org/10.1257/jep.26.1.3
- Okunan: özet ve çalışma kâğıdı sürümünün özeti. PDF: açık (MIT DSpace, eScholarship).
- Kârlı görünen verimlilik yatırımlarının piyasa aksaklıkları yüzünden yapılmadığı iddiasını
  ("verimlilik açığı") inceliyor; kanıtları toplayınca yaygın ve büyük bir açığın gösterilmesinin
  zor olduğu, politikaların hedefli olması gerektiği sonucuna varıyor. Mühendislik hesaplarının açığı
  abarttığını savunuyor (ACEEE gibi kurumlar bu varsayımlara itiraz ediyor).
- Projeyle ilişkisi: Duyarlılık analizimizde verimli ürünün fiyat farkını 12 yılda nadiren geri
  ödediğini bulduk; bu bulguyu tartışırken bağlam sağlıyor.

**[19] Kallbekken, S., Sælen, H., Hermansen, E. A. T. (2013). Bridging the Energy Efficiency Gap: A
Field Experiment on Lifetime Energy Costs and Household Appliances.** Journal of Consumer Policy,
36(1), s. 1–16. https://doi.org/10.1007/s10603-012-9211-z
- Okunan: özet. PDF: kütüphane (Springer).
- Bir elektronik perakendecisiyle doğal saha deneyi: ürünlere ömür boyu enerji maliyeti etiketi ve
  satış personeline eğitim. Kurutma makinelerinde satılan ürünlerin ortalama enerji tüketimi
  %4,9 (etiket + eğitim) azaldı, etki zamanla zayıfladı; buzdolabı–dondurucularda anlamlı etki yok.
- Projeyle ilişkisi: "Ömür boyu toplam maliyeti göstermek" GreenChoice'un temel fikri; bu çalışma
  etkisinin ürüne göre değişebildiğini ve sınırlı olabileceğini gösteriyor.

**[20] Waechter, S., Sütterlin, B., Siegrist, M. (2015). Desired and Undesired Effects of Energy
Labels—An Eye-Tracking Study.** PLoS ONE, 10(7), e0134132. https://doi.org/10.1371/journal.pone.0134132
- Okunan: özet ve yöntem. PDF: açık (PLOS).
- İsviçre'den 117 yetişkinle göz izleme deneyi: dört televizyon ve dört dondurucu arasında varsayımsal
  seçim; 2×2 denekler arası tasarım (etiket var/yok, kendine odak / tasarrufa odak). Etiket enerji
  bilgisine dikkati artırıyor ama seçimi pek değiştirmiyor; dikkati yıllık tüketimden verimlilik
  sınıfına kaydırıyor ("enerji verimliliği yanılgısı": yüksek sınıf düşük tüketim demek değil).
- Projeyle ilişkisi: Enerji kriterimizde sınıfı ve yıllık kWh'ı birlikte kullanmamızın ve açıklamada
  yıllık kWh'ı göstermemizin gerekçesi.

## Projeye çıkarımlar

- **Görev tanımı:** Sabit aspect listesiyle "aspect kategorisi + duygu" ([2], [3]); yorum başına 9
  etiketli çok etiketli sınıflandırma, alternatif olarak yardımcı cümle kurulumu ([6]).
- **Veri ve etiketleme:** Türkçe ABSA veri setleri var ([3], [7]) ama beyaz eşya için elle
  etiketlenmiş bir set bulunamadı. İki etiketçi ve kappa ([3], [17]).
- **Sınıf dengesizliği ve az veri:** Enerji ve servis yorumları çok az; sınıf ağırlıklı kayıp ([7]) ve
  doğrulama setinde eşik ayarı. ~300 eğitim yorumuyla BERTurk'ün kural tabanlı yöntemden ve TF-IDF'ten
  iyi olacağı varsayılmamalı, aynı test setinde karşılaştırılmalı.
- **Açıklama:** Ağırlıklı skorda katkılar doğrudan; ML skorlayıcıda SHAP ([11]) veya LIME ([10]).
  Açıklamaların değerlendirilmesi kullanıcı çalışmasıyla ([13], [14]).
- **Enerji ve maliyet:** Sınıf tek başına yanıltıcı olabilir ([20]); toplam maliyeti göstermenin
  etkisi sınırlı ve ürüne bağlı ([19]); verimli ürünlerin kendini ödediği varsayımı tartışmalı ([18]).
- **Boşluk:** Türkçe beyaz eşya yorumlarında aspect düzeyinde, enerji ve maliyet verisiyle birleştirilen
  açıklamalı bir karar destek çalışması bulunamadı. Arama kapsamlı değildi (genel web araması); rapordan
  önce Google Scholar ve DergiPark'ta tekrar bakılmalı.

## Colab denemesi

Defter: `notebooks/02_A_berturk_denemesi.ipynb` (uydurma cümlelerle; tokenizer, `[CLS]` temsili,
9 etiketli sınıflandırma başı ve 30 adımlık deneme eğitimi).

- [x] 07.11.2026'da Colab'da (T4 GPU seçilerek) hatasız çalıştı. Model indirildi, tokenizer ve
  9 etiketli sınıflandırma başı çalışıyor. Deneme eğitiminde kayıp 30 adımda 0,560'tan 0,235'e
  düştü (5. adım 0,560, 10. 0,431, 15. 0,373, 20. 0,348, 25. 0,288, 30. 0,235).
- Bu yalnızca kurulumun çalıştığını gösterir: 8 uydurma cümle ezberlendi, genelleme ölçülmedi.
- Süreler ve kullanılan GPU kaydedilmedi; A2.1'deki ilk gerçek eğitimde not edilecek.
