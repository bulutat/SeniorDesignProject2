"""Column layout of the data collection workbook (Excel) used for hand-collected data.

Only the columns a person really has to fill are shown; the exporter (sheets.py) writes the
remaining contract columns empty. `name` is the CSV column name used by the loaders.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Column:
    name: str
    label: str
    hint: str = ""
    required: bool = False
    choices: tuple[str, ...] = ()
    width: int = 16
    number_format: str = ""  # applied to every data row, so typed values never show as ####

DATE_FORMAT = "yyyy-mm-dd"
PRICE_FORMAT = "#,##0.00"


# Text people pick in the dropdowns -> value used by the pipeline
CATEGORY_LABELS = {"buzdolabı": "refrigerator", "çamaşır makinesi": "washing_machine"}
SOURCES = ("trendyol", "hepsiburada")

PILOT_COLUMNS = [
    Column("product_id", "Ürün no *", "ty-123456", True, width=14),
    Column("source", "Site *", "listeden seç", True, SOURCES, 14),
    Column("url", "Ürün adresi *", "https://...", True, width=38),
    Column("category", "Kategori *", "listeden seç", True, tuple(CATEGORY_LABELS), 18),
    Column("brand", "Marka", width=14),
    Column("model_code", "Model kodu *", "sitedeki model kodu", True, width=18),
    Column("name", "Ürün adı *", "sitedeki ad", True, width=44),
    Column("price_tl", "Fiyat (TL)", "sayı", width=16, number_format=PRICE_FORMAT),
    Column("energy_class", "Enerji sınıfı", "sitede yazan", width=14),
    Column("capacity", "Kapasite", "litre / kg", width=12),
    Column("rating_avg", "Puan", "1-5", width=10),
    Column("rating_count", "Değerlendirme sayısı", "sitede yazan", width=16),
]

EPREL_COLUMNS = [
    Column("model_code", "Model kodu *", "Trendyol'daki ile aynı", True, width=18),
    Column("product_group", "Ürün grubu", "adreste geçen ad", width=26),
    Column("energy_class", "Enerji sınıfı *", "A-G", True, tuple("ABCDEFG"), 12),
    Column("energy_kwh_per_year", "Yıllık enerji (kWh)", "buzdolabı", width=16),
    Column("energy_kwh_per_100_cycles", "100 yıkamada kWh", "çamaşır mak.", width=16),
    Column("water_l_per_cycle", "Yıkamada su (litre)", "çamaşır mak.", width=16),
    Column("noise_db", "Gürültü (dB)", width=14),
    Column("eprel_url", "EPREL sayfa adresi *", "https://eprel.ec.europa.eu/...", True, width=44),
    Column("collected_on", "Tarih", "2026-10-30", width=14, number_format=DATE_FORMAT),
    Column("note", "Not", "sayfada yazan etiket adı", width=34),
]

INSTRUCTIONS = [
    "Bu dosya iki tabloyu doldurmak içindir. Doldurduktan sonra komutla CSV'ye çevrilir.",
    "",
    "1) 'Ürünler' sayfası: Trendyol/Hepsiburada'daki ürünler. Her ürün için bir satır.",
    "   Turuncu başlıklı ve * işaretli alanlar zorunlu. Gri başlıklı alanları bilmiyorsan boş bırak.",
    "   Zorunlu alanı eksik olan ürünü yazma, başka ürüne geç (özellikle model kodu şart).",
    "2) 'EPREL' sayfası: aynı ürünlerin EPREL sayfasındaki değerleri. Model kodu 'Ürünler'dekiyle aynı olmalı.",
    "   Yalnızca EPREL sayfasında GÖRDÜĞÜN değeri yaz. Görmediğini boş bırak, tahmin etme.",
    "   EPREL'de bulamadığın ürün için satır ekleme. Ürünler sayfasında kalsın.",
    "3) Satır atlama, ortada boş satır bırakma. Veriler 3. satırdan başlar (1. satır başlık, 2. satır ipucu).",
    "4) Sayıları normal sayı olarak yaz (182,5 gibi). Ek yazı koyma (TL, kWh yazma).",
    "5) Bitince terminalde:",
    "   greenchoice import-sheets --xlsx data/raw/veri_toplama.xlsx --out-dir data/raw",
]
