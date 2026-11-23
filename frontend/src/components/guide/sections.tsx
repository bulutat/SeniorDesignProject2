import type { ReactElement } from "react";
import type { Category } from "../../types";
import { CRITERION_INFO } from "./criteria";

// Same values as defaults.label_thresholds in config/categories.yaml; update both together.
const RECOMMENDED_FROM = 70;
const NEUTRAL_FROM = 45;

type Body = (props: { category: Category | undefined }) => ReactElement;

function Start() {
  return (
    <>
      <p>
        GreenChoice, ev aletlerini yalnızca fiyata göre değil; enerji tüketimi, uzun vadeli maliyet,
        dayanıklılık ve kullanıcı deneyimine göre karşılaştırmanıza yardım eden bir karar destek
        aracıdır. Her ürün 0–100 arası bir skor alır ve skorun nedenleri açıkça gösterilir.
      </p>
      <h3>Nasıl kullanılır?</h3>
      <ol className="guide-steps">
        <li><strong>Kategori seçin.</strong> Üstteki sekmelerden buzdolabı veya çamaşır makinesini seçin.</li>
        <li>
          <strong>Listeyi daraltın.</strong> Ürün veya marka adıyla arayın; enerji sınıfına ve
          öneri durumuna göre filtreleyin; skora, fiyata veya enerji sınıfına göre sıralayın.
        </li>
        <li>
          <strong>Bir ürüne tıklayın.</strong> Sağdaki panelde fiyat, toplam maliyet, yıllık
          tüketim, skorun nedenleri ve her kriterin puanı görünür.
        </li>
        <li>
          <strong>Karşılaştırın.</strong> 2–4 ürünün yanındaki "Karşılaştır" kutusunu işaretleyin;
          ürünler bir tabloda yan yana gelir.
        </li>
        <li>
          <strong>Önceliklerinizi belirtin.</strong> "Sizin için hangi kriter ne kadar önemli?"
          bölümünde her kriteri "Önemli değil", "Önemli" veya "Çok önemli" olarak işaretleyip
          "Yeniden sırala"ya basın. Skorlar sizin önceliklerinize göre yeniden hesaplanır.
        </li>
      </ol>
    </>
  );
}

function Criteria({ category }: { category: Category | undefined }) {
  const criteria = category?.criteria ?? [];
  return (
    <>
      <p>
        Skor altı kriterden oluşur. Her kriter önce 0–100 arası bir alt puana çevrilir, sonra
        kategorinin ağırlıklarıyla birleştirilir.
        {category && <> Aşağıdaki ağırlıklar <strong>{category.name}</strong> kategorisinin varsayılanlarıdır.</>}
      </p>
      <dl className="guide-criteria">
        {criteria.map((c) => {
          const info = CRITERION_INFO[c.id];
          return (
            <div key={c.id}>
              <dt>
                {c.name}
                <span className="guide-weight">ağırlık %{Math.round(c.weight * 100)}</span>
              </dt>
              {info && (
                <dd>
                  <p>{info.measures}</p>
                  <p className="muted small"><strong>Kaynak:</strong> {info.source}</p>
                  <p className="muted small"><strong>Yüksek puan:</strong> {info.better}</p>
                </dd>
              )}
            </div>
          );
        })}
      </dl>
    </>
  );
}

function Reading() {
  return (
    <>
      <h3>Skor ve etiket</h3>
      <p>
        Skor, kriter puanlarının ağırlıklı toplamıdır (0–100). Etiket skora göre verilir:
      </p>
      <ul className="guide-labels">
        <li><span className="chip recommended">Önerilir</span> {RECOMMENDED_FROM} ve üzeri</li>
        <li><span className="chip neutral">Nötr</span> {NEUTRAL_FROM} ve üzeri, {RECOMMENDED_FROM}'in altı</li>
        <li><span className="chip not_recommended">Önerilmez</span> {NEUTRAL_FROM}'in altı</li>
      </ul>
      <h3>"Benzer ürünlere göre" ne demek?</h3>
      <p>
        Fiyat, toplam maliyet ve yıllık tüketim, aynı kategorideki ürünlerle kıyaslanarak puanlanır.
        Bu yüzden bir buzdolabının skoru bir çamaşır makinesininkiyle karşılaştırılamaz ve listeye
        yeni ürün eklendiğinde skorlar biraz değişebilir.
      </p>
      <h3>"Neden bu skor?" bölümü</h3>
      <p>
        Skoru en çok etkileyen en fazla dört kriter listelenir. Baştaki sayı, o kriterin ürünün
        skorunu kategori ortalamasına göre kaç puan <span className="pos">yukarı (+)</span> veya{" "}
        <span className="neg">aşağı (−)</span> çektiğini gösterir. Etkisi 1 puanın altında kalan
        kriterler gösterilmez.
      </p>
      <h3>"(veri yok)" işareti</h3>
      <p>
        Bir ürünün bir kriter için verisi yoksa (ör. hiç yorumu yoksa) o kriter kategorinin orta
        değeriyle (medyan) doldurulur. Böylece eksik veri ürünü belirgin şekilde öne çıkarmaz ya da
        geriye atmaz. Doldurulan kriterler
        <span className="nowrap">"(veri yok)"</span> diye işaretlenir ve skorun nedenleri arasında kullanılmaz.
      </p>
      <h3>Toplam maliyet</h3>
      <p>
        Detaydaki "… yıllık toplam maliyet", satın alma fiyatına ürün ömrü boyunca ödenecek elektrik ve
        su giderinin eklenmesiyle bulunur. Fiyatı yüksek ama az tüketen bir ürün, uzun vadede daha
        ucuza gelebilir.
      </p>
    </>
  );
}

function Limits() {
  return (
    <>
      <p>GreenChoice bir öğrenci projesi prototipidir. Sonuçları yorumlarken şunları göz önünde tutun:</p>
      <ul className="guide-list">
        <li>Fiyatlar veri toplandığı tarihe aittir; güncel fiyat mağazada farklı olabilir.</li>
        <li>
          Elektrik ve su giderleri vergiler hariç resmi tarifelerle ve ortalama bir hane kullanımıyla
          hesaplanır; sizin faturanız farklı olabilir.
        </li>
        <li>Ürün ömrü her kategori için sabit bir varsayımdır (detay panelinde yazan yıl sayısı).</li>
        <li>
          Yorum tabanlı kriterler otomatik metin analizine dayanır ve hata yapabilir. Az yorumu olan
          ürünlerde bu kriterlerin güvenilirliği düşüktür.
        </li>
        <li>
          Skor bir öneridir, kesin hüküm değildir. Size en uygun ürün; ihtiyacınıza, bütçenize ve
          önceliklerinize göre değişir.
        </li>
      </ul>
      <p className="muted small">
        Detay panelinin altındaki "Yöntem" satırı, skoru hangi modelin ürettiğini gösterir.
      </p>
    </>
  );
}

export const GUIDE_TABS = [
  { id: "start", label: "Başlarken", Body: Start as Body },
  { id: "criteria", label: "Kriterler", Body: Criteria as Body },
  { id: "reading", label: "Sonuçları okuma", Body: Reading as Body },
  { id: "limits", label: "Veri ve sınırlar", Body: Limits as Body },
] as const;

export type GuideTab = (typeof GUIDE_TABS)[number]["id"];
