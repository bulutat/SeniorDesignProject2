// Turkish interface texts (source language). en.ts and de.ts must have the same shape:
// they are typed as Messages, so a missing or extra key fails `tsc`.
// Product data (names, brands, prices in TL) is never translated.
import type { Label } from "../types";

export const tr = {
  locale: "tr-TR",
  app: {
    subtitle: "Ürünleri fiyatın yanında enerji, uzun vadeli maliyet ve dayanıklılığa göre karşılaştırın.",
    categoriesNav: "Kategoriler",
    language: "Dil",
    help: "Nasıl kullanılır?",
    pickProduct: "Ayrıntıları ve skorun nedenlerini görmek için bir ürün seçin.",
    howToRead: "Skorlar nasıl yorumlanır?",
    noMatch: "Bu filtrelere uyan ürün yok.",
    loading: "Yükleniyor…",
    requestFailed: (status: number) => `İstek başarısız: ${status}`,
  },
  labels: {
    recommended: "Önerilir",
    neutral: "Nötr",
    not_recommended: "Önerilmez",
  } as Record<Label, string>,
  list: {
    search: "Ürün veya marka ara…",
    energyFilter: "Enerji sınıfı",
    allEnergy: "Tüm enerji sınıfları",
    energyOption: (c: string) => `Enerji sınıfı ${c}`,
    labelFilter: "Öneri durumu",
    allLabels: "Tüm öneriler",
    sort: "Sıralama",
    sortScore: "Sırala: Skor",
    sortPriceAsc: "Sırala: Fiyat ↑",
    sortPriceDesc: "Sırala: Fiyat ↓",
    sortEnergy: "Sırala: Enerji (A→G)",
    count: (shown: number, total: number) => `${shown} / ${total} ürün`,
    clear: "Filtreleri temizle",
    energyClass: "Enerji sınıfı",
    compare: "Karşılaştır",
  },
  weights: {
    title: "Sizin için hangi kriter ne kadar önemli?",
    none: "Önemli değil",
    normal: "Önemli",
    high: "Çok önemli",
    pickOne: "En az bir kriteri \"Önemli\" veya \"Çok önemli\" seçin.",
    apply: "Yeniden sırala",
    reset: "Varsayılana dön",
  },
  detail: {
    price: "Fiyat",
    tco: (years: number) => `${years} yıllık toplam maliyet`,
    annual: "Yıllık tüketim",
    energyClass: "Enerji sınıfı",
    why: "Neden bu skor?",
    criteria: "Kriter puanları",
    noData: "(veri yok)",
    footer: (n: number, method: string) => `${n} yorum analiz edildi · Yöntem: ${method}`,
  },
  compare: {
    title: "Karşılaştırma",
    score: "GreenChoice skoru",
    price: "Fiyat",
    tco: "Toplam maliyet",
    kwh: "Yıllık kWh",
  },
  guide: {
    title: "GreenChoice rehberi",
    close: "Rehberi kapat",
    sections: "Rehber bölümleri",
    tabs: { start: "Başlarken", criteria: "Kriterler", reading: "Sonuçları okuma", limits: "Veri ve sınırlar" },
    start: {
      intro:
        "GreenChoice, ev aletlerini yalnızca fiyata göre değil; enerji tüketimi, uzun vadeli maliyet, " +
        "dayanıklılık ve kullanıcı deneyimine göre karşılaştırmanıza yardım eden bir karar destek aracıdır. " +
        "Her ürün 0–100 arası bir skor alır ve skorun nedenleri açıkça gösterilir.",
      howTitle: "Nasıl kullanılır?",
      steps: [
        ["Kategori seçin.", "Üstteki sekmelerden buzdolabı veya çamaşır makinesini seçin."],
        ["Listeyi daraltın.", "Ürün veya marka adıyla arayın; enerji sınıfına ve öneri durumuna göre filtreleyin; skora, fiyata veya enerji sınıfına göre sıralayın."],
        ["Bir ürüne tıklayın.", "Sağdaki panelde fiyat, toplam maliyet, yıllık tüketim, skorun nedenleri ve her kriterin puanı görünür."],
        ["Karşılaştırın.", "2–4 ürünün yanındaki \"Karşılaştır\" kutusunu işaretleyin; ürünler bir tabloda yan yana gelir."],
        ["Önceliklerinizi belirtin.", "\"Sizin için hangi kriter ne kadar önemli?\" bölümünde her kriteri \"Önemli değil\", \"Önemli\" veya \"Çok önemli\" olarak işaretleyip \"Yeniden sırala\"ya basın. Skorlar sizin önceliklerinize göre yeniden hesaplanır."],
        ["Dili değiştirin.", "Sağ üstteki dil menüsünden Türkçe, English veya Deutsch seçin. Ürün adları ve TL fiyatlar mağazadaki haliyle kalır."],
      ] as [string, string][],
    },
    criteria: {
      intro: "Skor altı kriterden oluşur. Her kriter önce 0–100 arası bir alt puana çevrilir, sonra kategorinin ağırlıklarıyla birleştirilir.",
      defaults: (category: string) => `Aşağıdaki ağırlıklar ${category} kategorisinin varsayılanlarıdır.`,
      weight: (pct: number) => `ağırlık %${pct}`,
      source: "Kaynak:",
      better: "Yüksek puan:",
    },
    info: {
      energy_efficiency: {
        measures: "Ürünün enerji sınıfı (2021 AB ölçeği, A en iyi, G en kötü) ile yıllık elektrik tüketiminin (kWh) ortalaması. Yıllık tüketim, aynı kategorideki ürünlere göre değerlendirilir.",
        source: "EPREL (AB enerji etiketi veritabanı), üreticinin resmi enerji etiketi veya mağaza bilgisi.",
        better: "Sınıf A'ya yakın ve yıllık kWh düşük olan ürün daha yüksek puan alır.",
      },
      lifetime_cost: {
        measures: "Ürünün ömrü boyunca toplam maliyeti: satın alma fiyatı + ömür (yıl) × yıllık elektrik ve su gideri. Çamaşır makinesinde yıllık tüketim, etiketteki 100 yıkama başına değerden hesaplanır.",
        source: "Fiyat mağazadan; elektrik birim fiyatı EPDK tarifesinden, su birim fiyatı İSKİ tarifesinden (vergiler hariç).",
        better: "Toplam maliyeti benzer ürünlerden düşük olan ürün daha yüksek puan alır.",
      },
      durability: {
        measures: "Kullanıcı yorumlarında dayanıklılıktan olumlu ve olumsuz söz edilme dengesi. Yorumlar otomatik olarak analiz edilir.",
        source: "Mağaza sayfalarındaki kullanıcı yorumları.",
        better: "Dayanıklılıktan olumlu bahseden yorumların ağır bastığı ürün daha yüksek puan alır.",
      },
      service: {
        measures: "Servis veya arıza şikâyeti içeren yorumların, ürünün tüm yorumlarına oranı.",
        source: "Mağaza sayfalarındaki kullanıcı yorumları.",
        better: "Şikâyet oranı düşük olan ürün daha yüksek puan alır.",
      },
      price_advantage: {
        measures: "Satış fiyatının aynı kategorideki ürünlere göre konumu.",
        source: "Veri toplandığı tarihteki mağaza fiyatı.",
        better: "Benzerlerine göre ucuz olan ürün daha yüksek puan alır.",
      },
      satisfaction: {
        measures: "Mağazadaki ortalama yıldız puanı (1–5). Az değerlendirmesi olan ürünlerin puanı kategori ortalamasına doğru çekilir, böylece birkaç oyla alınan 5 yıldız tek başına öne geçmez.",
        source: "Mağaza puanı; yoksa yorumların ortalaması.",
        better: "Çok sayıda değerlendirmede yüksek ortalaması olan ürün daha yüksek puan alır.",
      },
    } as Record<string, { measures: string; source: string; better: string }>,
    reading: {
      scoreTitle: "Skor ve etiket",
      scoreText: "Skor, kriter puanlarının ağırlıklı toplamıdır (0–100). Etiket skora göre verilir:",
      recommendedRange: (from: number) => `${from} ve üzeri`,
      neutralRange: (from: number, to: number) => `${from} ve üzeri, ${to}'in altı`,
      notRecommendedRange: (below: number) => `${below}'in altı`,
      similarTitle: "\"Benzer ürünlere göre\" ne demek?",
      similarText: "Fiyat, toplam maliyet ve yıllık tüketim, aynı kategorideki ürünlerle kıyaslanarak puanlanır. Bu yüzden bir buzdolabının skoru bir çamaşır makinesininkiyle karşılaştırılamaz ve listeye yeni ürün eklendiğinde skorlar biraz değişebilir.",
      whyTitle: "\"Neden bu skor?\" bölümü",
      whyBefore: "Skoru en çok etkileyen en fazla dört kriter listelenir. Baştaki sayı, o kriterin ürünün skorunu kategori ortalamasına göre kaç puan",
      up: "yukarı (+)",
      or: "veya",
      down: "aşağı (−)",
      whyAfter: "çektiğini gösterir. Etkisi 1 puanın altında kalan kriterler gösterilmez.",
      noDataTitle: "\"(veri yok)\" işareti",
      noDataText: "Bir ürünün bir kriter için verisi yoksa (ör. hiç yorumu yoksa) o kriter kategorinin orta değeriyle (medyan) doldurulur. Böylece eksik veri ürünü belirgin şekilde öne çıkarmaz ya da geriye atmaz. Doldurulan kriterler \"(veri yok)\" diye işaretlenir ve skorun nedenleri arasında kullanılmaz.",
      tcoTitle: "Toplam maliyet",
      tcoText: "Detaydaki \"… yıllık toplam maliyet\", satın alma fiyatına ürün ömrü boyunca ödenecek elektrik ve su giderinin eklenmesiyle bulunur. Fiyatı yüksek ama az tüketen bir ürün, uzun vadede daha ucuza gelebilir.",
    },
    limits: {
      intro: "GreenChoice bir öğrenci projesi prototipidir. Sonuçları yorumlarken şunları göz önünde tutun:",
      items: [
        "Fiyatlar veri toplandığı tarihe aittir; güncel fiyat mağazada farklı olabilir.",
        "Elektrik ve su giderleri vergiler hariç resmi tarifelerle ve ortalama bir hane kullanımıyla hesaplanır; sizin faturanız farklı olabilir.",
        "Ürün ömrü her kategori için sabit bir varsayımdır (detay panelinde yazan yıl sayısı).",
        "Yorum tabanlı kriterler otomatik metin analizine dayanır ve hata yapabilir. Az yorumu olan ürünlerde bu kriterlerin güvenilirliği düşüktür.",
        "Ürün adları mağazadaki orijinal (Türkçe) halleriyle gösterilir; fiyatlar Türk lirasıdır (TL) ve başka para birimine çevrilmez.",
        "Skor bir öneridir, kesin hüküm değildir. Size en uygun ürün; ihtiyacınıza, bütçenize ve önceliklerinize göre değişir.",
      ],
      method: "Detay panelinin altındaki \"Yöntem\" satırı, skoru hangi modelin ürettiğini gösterir.",
    },
  },
};

export type Messages = typeof tr;
