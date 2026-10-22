# GreenChoice

Yapay zekâ tabanlı sürdürülebilir ve bilinçli ürün seçim sistemi.
COMP 491 bitirme projesi · 2026–2027 Güz · Atahan Bulut, Ali Rubar Kal · Danışman: Tuna Çakar

Ürünleri yalnızca fiyata göre değil; enerji tüketimi, uzun vadeli kullanım maliyeti,
dayanıklılık ve kullanıcı deneyimine göre değerlendiren, skorunun nedenlerini de açıklayan
bir karar destek sistemi prototipi.

> Şu anki durum: **iskelet**. Pipeline, API ve arayüz `data/sample/` altındaki
> **sentetik** veriyle uçtan uca çalışıyor. Gerçek veri toplama (Aşama 1), BERTurk (Aşama 2),
> ML modelleri (Aşama 3) ve SHAP (Aşama 4) için yerler hazır, içleri boş.

## Klasör yapısı

```
config/          kategoriler, kriter ağırlıkları, aspect anahtar ifadeleri (YAML)
data/
  sample/        sentetik örnek veri (repoda)
  annotations/   manuel etiketler (repoda)
  raw/ interim/ processed/   toplanan ve üretilen veri (repoya girmez)
docs/            mimari, veri ve API sözleşmeleri, kararlar, etiketleme kılavuzu, takvim
frontend/        React + Vite arayüzü
notebooks/       keşif / deney notebook'ları
src/greenchoice/
  collect/       veri toplama (e-ticaret, EPREL)
  preprocess/    temizleme, EPREL eşleştirme, TCO
  nlp/           aspect çıkarımı, toplulaştırma, P/R/F1
  scoring/       kriter alt skorları, ağırlıklı baseline, ML karşılaştırma
  explain/       açıklama cümleleri
  api/           FastAPI
  pipeline.py    uçtan uca komut satırı
tests/           pytest
```

Ayrıntılı mimari: [docs/architecture.md](docs/architecture.md)

## Kurulum

Gerekenler: Python 3.11+, Node.js 20+, Git.

```bash
# Python ortamı (proje klasöründe)
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell / cmd)
# source .venv/bin/activate      # macOS / Linux
pip install -e ".[dev,ml,scrape]"

# Frontend
cd frontend
npm install
```

BERTurk için (Aşama 2, büyük indirme): `pip install -e ".[nlp]"`

## Çalıştırma

```bash
# 1) Veritabanını üret (örnek veriyle)
greenchoice build

# 2) API'yi başlat  ->  http://localhost:8000/docs
uvicorn greenchoice.api.main:app --reload

# 3) Arayüzü başlat (ayrı terminalde)  ->  http://localhost:5173
cd frontend
npm run dev
```

Gerçek veriyle: `greenchoice build --source interim --eprel data/raw/eprel.csv`

## Test

```bash
pytest
ruff check src tests
```

## Dokümanlar

- [Mimari](docs/architecture.md)
- [Veri sözleşmeleri](docs/data-contracts.md)
- [API](docs/api.md)
- [Karar kaydı](docs/decisions.md)
- [Etiketleme kılavuzu](docs/annotation-guideline.md)
- [Görev dağılımı](docs/gorev-dagilimi.md)
- [Proje takvimi (Gantt)](docs/takvim.html)
- [Çalışma kuralları](CONTRIBUTING.md)
