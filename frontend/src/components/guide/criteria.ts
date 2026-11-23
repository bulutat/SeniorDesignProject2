// Plain-language description of each scoring criterion for the guide.
// Must describe what src/greenchoice/scoring/criteria.py and preprocess/tco.py actually do;
// update both together. Criterion names and weights come from the API, not from here.

export interface CriterionInfo {
  measures: string;
  source: string;
  better: string;
}

export const CRITERION_INFO: Record<string, CriterionInfo> = {
  energy_efficiency: {
    measures:
      "Ürünün enerji sınıfı (2021 AB ölçeği, A en iyi, G en kötü) ile yıllık elektrik " +
      "tüketiminin (kWh) ortalaması. Yıllık tüketim, aynı kategorideki ürünlere göre değerlendirilir.",
    source: "EPREL (AB enerji etiketi veritabanı), üreticinin resmi enerji etiketi veya mağaza bilgisi.",
    better: "Sınıf A'ya yakın ve yıllık kWh düşük olan ürün daha yüksek puan alır.",
  },
  lifetime_cost: {
    measures:
      "Ürünün ömrü boyunca toplam maliyeti: satın alma fiyatı + ömür (yıl) × yıllık elektrik " +
      "ve su gideri. Çamaşır makinesinde yıllık tüketim, etiketteki 100 yıkama başına değerden " +
      "hesaplanır.",
    source: "Fiyat mağazadan; elektrik birim fiyatı EPDK tarifesinden, su birim fiyatı İSKİ " +
      "tarifesinden (vergiler hariç).",
    better: "Toplam maliyeti benzer ürünlerden düşük olan ürün daha yüksek puan alır.",
  },
  durability: {
    measures:
      "Kullanıcı yorumlarında dayanıklılıktan olumlu ve olumsuz söz edilme dengesi. Yorumlar " +
      "otomatik olarak analiz edilir.",
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
    measures:
      "Mağazadaki ortalama yıldız puanı (1–5). Az değerlendirmesi olan ürünlerin puanı kategori " +
      "ortalamasına doğru çekilir, böylece birkaç oyla alınan 5 yıldız tek başına öne geçmez.",
    source: "Mağaza puanı; yoksa yorumların ortalaması.",
    better: "Çok sayıda değerlendirmede yüksek ortalaması olan ürün daha yüksek puan alır.",
  },
};
