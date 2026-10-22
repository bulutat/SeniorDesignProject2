# Çalışma kuralları

## Git akışı

- `main` her zaman çalışır durumda kalır; doğrudan `main`'e commit atılmaz.
- Her iş için dal açın: `<kişi>/<konu>` → ör. `atahan/yorum-scraper`, `ali/eprel-eslestirme`.
- İş bitince Pull Request açın. **Diğer kişi inceleyip onaylar**, sonra birleştirilir.
- PR açmadan önce: `pytest` geçmeli; frontend'e dokunduysanız `npm run build` çalışmalı.

## Commit mesajları

Kısa, Türkçe veya İngilizce, ne yapıldığını söyleyen: `EPREL eşleştirmesi eklendi`,
`BERTurk eğitim script'i`, `fix: TCO'da su maliyeti`.

## Kod

- Python kodu `src/greenchoice/` altında. Notebook'tan kalıcı olacak kod buraya taşınır.
- Veri sözleşmeleri (`contracts.py`, `schemas.py`, `frontend/src/types.ts`) değişecekse
  önce diğer kişiye haber verin, `docs/data-contracts.md` veya `docs/api.md`'yi güncelleyin.
- Yeni bir fonksiyonun en az bir testi olsun (`tests/`).
- Ham ve işlenmiş veri repoya girmez (`.gitignore`). Manuel etiketler (`data/annotations/`) girer.
- API anahtarları `.env` dosyasına; `.env` repoya girmez.

## Haftalık rutin

- Danışman toplantısı notları: `docs/meetings/YYYY-MM-DD.md`
- Önemli kararlar: `docs/decisions.md`
