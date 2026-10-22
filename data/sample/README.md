# Örnek veri (sentetik)

Bu klasördeki ürünler, markalar ve yorumlar **uydurmadır**. Gerçek veri gelene kadar
pipeline'ı, API'yi ve arayüzü uçtan uca çalıştırmak için kullanılır. Rapora veya
sonuçlara girmez.

Bilerek eklenen durumlar (temizleme ve eksik veri kodunu sınamak için):

- `s-rf-06`: Türkçe biçimli fiyat (`"19.999,00 TL"`) ve 2021 öncesi enerji sınıfı (`A++`).
  Sınıf boş bırakılır, enerji alt skoru yalnızca kWh'den hesaplanır.
- `s-wm-06`: Puan ve gürültü bilgisi yok, iki yorumu da temizlemede atılacak kadar kısa.
  Yorum tabanlı kriterler ve memnuniyet kategori medyanıyla doldurulur, açıklamada kullanılmaz.
- `r017`: tekrar eden kelimelerden oluşan spam yorum (temizlemede atılır).
- `r041`: `r040`'ın kopyası (temizlemede atılır).
- `r046`, `r047`: 10 karakterden kısa yorumlar (temizlemede atılır).
