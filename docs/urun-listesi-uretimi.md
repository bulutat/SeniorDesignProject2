# Ürün listesini üretme (80 ürün) — adım adım

Bu belge, `data/toplanan/veri_toplama_v4.xlsx` dosyasının nasıl üretildiğini ve yeniden nasıl
üretileceğini anlatır. Kurallar: karar 17 (toplama yöntemi), 18 (seçim kuralı), 19 (neyin Git'e
gireceği). Her adım bir komuttur; tek seferlik betik yoktur.

```
kaydedilen Hepsiburada sayfaları ──import-listings──▶ aday_urunler.csv ─┐
Trendyol ürün adresleri ──────────fetch-trendyol────▶ trendyol_adaylar.json ─┤
                                                        select-candidates ──▶ secilen_urunler.csv
secilen_urunler.csv + eprel_kayitlari.json + önceki Excel ──append-selection──▶ yeni Excel
yeni Excel ──import-sheets──▶ pilot_products.csv + eprel_manual.csv ──check-pilot──▶ rapor + Kişi A'ya liste
```

## 1. Hepsiburada: sayfaları kaydet, ayrıştır

Hepsiburada otomatik isteğe CAPTCHA ile cevap verir, bu yüzden scraper yoktur (karar 17a).

1. Tarayıcıda kategori arama sayfalarını aç (ör. çamaşır makinesi, buzdolabı; birkaç sayfa).
2. `Ctrl+S` ile "Web Sayfası, Tamamı" olarak `data/raw/listeleme_sayfalari/` altına kaydet.
   Bu klasör Git'e girmez (telifli içerik, ~200 MB).
3. ```bash
   greenchoice import-listings --pages data/raw/listeleme_sayfalari --out data/interim/aday_urunler.csv
   ```

## 2. Trendyol: bilinen ürün adreslerini oku

Arama ve yorum API'si kullanılmaz (robots.txt yasaklıyor). Adresleri tarayıcıdan sen toplarsın;
komut yalnızca o ürün sayfalarını, robots.txt'ye uyarak, en az 2 sn arayla okur. Paylaşım
bağlantısındaki `?boutiqueId=...` gibi parametreler komut tarafından atılır.

```bash
greenchoice fetch-trendyol --category washing_machine --url <adres1> <adres2> --out data/interim/trendyol_camasir.json
greenchoice fetch-trendyol --category refrigerator --url <adres1> <adres2> --out data/interim/trendyol_buzdolabi.json
```

Kategori başına çıkan dosyalar `select-candidates --trendyol` ile tek dosyada kullanılmak
isteniyorsa JSON listeleri birleştirilir (`trendyol_adaylar.json` bu şekilde oluştu).

## 3. Seçim

```bash
greenchoice select-candidates --listings data/interim/aday_urunler.csv --trendyol data/interim/trendyol_adaylar.json --existing data/raw/pilot_products.csv --out data/interim/secilen_urunler.csv
```

Kural karar 18'dedir (kategori başına hedef 40, en az 30 değerlendirme, marka başına en fazla 12,
mini/ofis tipi hariç, aynı model tek kayıt). Çıktıdaki `shortfall` değerine bak: hedefe ulaşılmadıysa
kaynak sayfa eklemek gerekir, kuralı gevşetme.

## 4. EPREL kayıtlarını bul ve oku

EPREL eşleşmesi seçim kriteri değildir, bulgudur (karar 17c). Yine de seçilen ürünlerin model
kodları EPREL'de aranır. EPREL API'si anahtar istediği için kayıtlar sitenin herkese açık arama
ve kayıt sayfalarından, elle okunur (`docs/eprel-manual-toplama.md`).

1. EPREL sitesinde ilgili ürün grubunun arama sayfasını aç, "include old products" kutusunu işaretle.
   Model arama alanı tam eşleşme (exact) arar. Mağaza kodunun sonundaki pazar eki (`...AH`, `...TR`)
   EPREL'de olmayabilir: önce olduğu gibi, sonra son iki harf atılmış hâlini ara.
2. Kayıt numarasını bulmak için, arama sayfası açıkken tarayıcı konsoluna aşağıdaki yardımcı
   yapıştırılır. Aranan kodları yazar, her arama arasında 2,3 sn bekler ve sonuç kartlarındaki
   `res_compareModel_<kayıt no>` değerini döndürür. Yalnızca kayıt numarası bulur, değer okumaz.
   ```js
   window.__ids=async(codes)=>{
   const setVal=(el,v)=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,v); el.dispatchEvent(new Event('input',{bubbles:true}));};
   const norm=s=>s.replace(/\s/g,'').toUpperCase();
   const res={};
   for(const c of codes){
     setVal(Array.from(document.querySelectorAll('input[type=text]'))[0],c);
     Array.from(document.querySelectorAll('button')).find(x=>/^\s*search\s*$/i.test(x.innerText)).click();
     await new Promise(r=>setTimeout(r,2300));
     const cards=Array.from(document.querySelectorAll('app-search-result-card')).filter(k=>k.innerText.split('\n').some(l=>norm(l)===norm(c)));
     res[c]=cards.map(k=>{const m=k.outerHTML.match(/res_compareModel_(\d+)/);return m?m[1]:null}).filter(Boolean);
   }
   return res;};
   window.__ids(['KGN55CIE0N','WW90CGC04DAE'])
   ```
   Boş dizi dönen kod EPREL'de bulunamamıştır (eşleşmeyen ürün; listede kalır). Birden fazla
   numara dönerse kayıtları kendin karşılaştır.
3. Kayıt sayfası: `https://eprel.ec.europa.eu/screen/product/<grup>/<kayıt no>`. Grup
   `washingmachines2019` (çamaşır makinesi) veya `refrigeratingappliances2019` (buzdolabı).
   Değerleri sayfadan **gördüğün gibi** oku:

   | Kategori | Okunan alanlar (sayfadaki etiket) |
   |---|---|
   | Çamaşır makinesi | "Weighted energy consumption (per 100 cycles, eco 40-60 programme)", "Water consumption (per cycle…)", gürültü (spinning phase), "Rated capacity" |
   | Buzdolabı | "Annual energy consumption", "Total volume", gürültü |

   Enerji sınıfı etiket görselinin dosya adından okunur. Buzdolabı sayfasında ayrıca aydınlatma
   kaynağı sınıfı yazar, onu kullanma. Sayfa "artık piyasada değil" diyorsa `off_market` true olur.
4. Okuduğun kaydı `data/toplanan/eprel_kayitlari.json` dosyasına ekle. Alanlar ve örnek için
   dosyadaki mevcut kayıtlara bak. Yükleyici (`load_records`) kategori/grup uyumunu, enerji
   sınıfını (A-G), tekrar eden kodu denetler; hatalı kayıtta kayıt sırasıyla durur.
   Değeri okuyamadığın alanı `null` bırak, tahmin etme.

## 5. Excel'e ekle

```bash
greenchoice append-selection --base data/raw/veri_toplama_birlesik_v3.xlsx --selection data/interim/secilen_urunler.csv --records data/toplanan/eprel_kayitlari.json --out data/raw/veri_toplama_v4.xlsx
```

- Mevcut Excel değişmez, yeni dosya yazılır (`--out` ile `--base` aynı olamaz).
- Ürünün model kodu: EPREL kaydı bulunduysa EPREL kimliği, bulunmadıysa başlıktaki ilk kod,
  hiç kod yoksa boş. Kapasite yalnızca EPREL kaydından gelir.
- `Ürünler` sayfasında zaten olan `product_id` atlanır; `EPREL` sayfasında zaten olan model için
  satır eklenmez. Komutu iki kez çalıştırmak güvenlidir.
- Çıktıdaki özet `matched` / `unmatched_with_code` / `no_code` sayılarını verir. 80 ürünlük
  listede 48 ürün (%60) EPREL ile eşleşti; hedef %70 idi, bu rapor için bir bulgudur (karar 17c).
- Excel'i aç, ürünleri gözle kontrol et (özellikle Trendyol'dan gelenleri), gerekirse elle düzelt.

## 6. Doğrula ve Kişi A'ya ver

```bash
greenchoice import-sheets --xlsx data/raw/veri_toplama_v4.xlsx --out-dir data/raw
greenchoice check-pilot --products data/raw/pilot_products.csv --eprel data/raw/eprel_manual.csv --out data/interim/pilot_products.csv
```

`check-pilot` zorunlu alan, sayı aralığı ve fiyat eşiği hatalarında satır numarasıyla durur.
`data/interim/pilot_products.csv` (yalnızca `product_id`, `url`, `category`) Kişi A'nın yorum
toplama listesidir; Git'e girmesine izin verilen tek `interim` dosyasıdır.

## Neleri yedekle

Git'e girmeyen ve yeniden üretilmesi zahmetli olanlar: `data/raw/listeleme_sayfalari/`,
`data/raw/http_cache/` (yorum yazarı adı içerir, paylaşma), eski Excel sürümleri
(`data/raw/veri_toplama*.xlsx`). Küçük, olgusal çıktılar `data/toplanan/` altında Git'tedir
(karar 19).
