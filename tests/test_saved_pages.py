"""Saved review pages. The HTML below is synthetic: it copies the structure of real saved
pages (inspected 2026-11-01) with invented text, so no user content enters the repository."""

import json

import pytest

from greenchoice.collect.saved_pages import import_folder, parse_page

TY_URL = "https://www.trendyol.com/marka/urun-p-111/yorumlar"
HB_URL = "https://www.hepsiburada.com/marka-urun-pm-HBCAAA-yorumlari"


def ty_review(comment_id, text, padding="0px", date=("19", "Ağustos", "2026"), truncated=False):
    day, month, year = date
    more = '<button class="read-more">Devamını Oku</button>' if truncated else ""
    return f"""<div class="review"><div class="review-info">
      <div class="star-rating-star-container review-stars" data-testid="star-rating">
      <div class="star-rating-full-star" style="padding-inline-end: {padding};"></div></div>
      <div class="review-info-detail"><div class="detail-item name">G** İ**</div>
      <div class="detail-item date"><span>{day}</span><span>{month}</span><span>{year}</span></div>
      </div></div>
      <div class="review-comment"><div class="comment-body{comment_id}">
      <span class="review-comment"><span>{text}</span></span>{more}</div></div></div>"""


def ty_page(reviews, comment_count=2):
    return f"""<!-- saved from url=(0049){TY_URL} --><html><head>
      <link rel="canonical" href="{TY_URL}"></head><body>
      <script>window.x={{"ratingScore":{{"averageRating":4.5,"commentCount":{comment_count},
      "totalCount":9}}}}</script>{"".join(reviews)}</body></html>"""


def hb_card(text, stars=5, date="2026-02-12", aspects=()):
    filled = '<div class="star" style="width:12px"></div>' * stars
    empty = '<div class="outlinedStar" style="width:12px"></div>' * (5 - stars)
    body = f"<span>{text}</span>" if text else ""
    block = ""
    if aspects:
        pairs = "".join(f'<span class="a">{k}</span><span class="a">{v}</span>' for k, v in aspects)
        block = f'<div><span class="b">Değerlendirilen özellikler</span><div>{pairs}</div></div>'
    return f"""<div class="card"><div>{filled}{empty}</div>
      <span class="d" content="{date}">12 Şubat, Per</span><span class="u">G**** İ****</span>
      <div>{body}{block}</div></div>"""


def hb_page(cards, page=1, total=2):
    return f"""<html><head><link rel="canonical" href="{HB_URL}"></head><body>
      <div class="paginationOverlay"><div class="paginationContentHolder">{"".join(cards)}</div>
      <div class="paginationBarHolder">1 2 Önceki {page} / {total} Sonraki</div></div></body></html>"""


def test_trendyol_page_is_parsed_without_the_username():
    html = ty_page([ty_review(1, "Çok sessiz çalışıyor"),
                    ty_review(2, "Kısa sürede bozuldu", padding="66.8571px", truncated=True)])
    page = parse_page(html, "a.html")
    assert page.product_id == "ty-111" and page.site_total == 2
    first, second = page.reviews
    assert first["review_id"] == "ty-1" and first["rating"] == 5
    assert first["date"] == "2026-08-19" and first["text"] == "Çok sessiz çalışıyor"
    assert second["rating"] == 1 and second["truncated"] and "Devamını" not in second["text"]
    assert "G**" not in json.dumps(page.reviews, ensure_ascii=False)


def test_trendyol_star_width_that_does_not_fit_fails_loudly():
    with pytest.raises(ValueError, match="a.html"):
        parse_page(ty_page([ty_review(1, "metin", padding="20px")]), "a.html")


def test_hepsiburada_page_reads_rating_date_aspects_and_counts_empty_cards():
    html = hb_page([hb_card("Enerji tüketimi az", stars=4, aspects=[("Enerji Tüketimi", "5")]),
                    hb_card("", stars=5)])
    page = parse_page(html, "b.html")
    assert page.product_id == "hb-HBCAAA" and (page.page, page.total_pages) == (1, 2)
    assert page.cards == 2 and len(page.reviews) == 1
    review = page.reviews[0]
    assert review["rating"] == 4 and review["date"] == "2026-02-12"
    assert json.loads(review["site_aspects"]) == {"Enerji Tüketimi": 5}
    assert review["review_id"].startswith("hb-")
    assert "G**" not in json.dumps(page.reviews, ensure_ascii=False)


def test_page_without_reviews_fails_with_the_file_name():
    html = f'<html><head><link rel="canonical" href="{TY_URL}"></head></html>'
    with pytest.raises(ValueError, match="bos.html"):
        parse_page(html, "bos.html")


def test_unknown_site_fails():
    html = '<html><head><link rel="canonical" href="https://example.com/x"></head></html>'
    with pytest.raises(ValueError, match="x.html"):
        parse_page(html, "x.html")


def write(folder, name, html):
    (folder / name).write_text(html, encoding="utf-8")


def test_import_folder_merges_pages_drops_duplicates_and_reports_gaps(tmp_path):
    write(tmp_path, "t.html", ty_page([ty_review(1, "Sessiz"), ty_review(2, "Güzel")], comment_count=5))
    write(tmp_path, "t2.html", ty_page([ty_review(1, "Sessiz")], comment_count=5))
    write(tmp_path, "h1.html", hb_page([hb_card("Dayanıklı")], page=1, total=2))
    table, report = import_folder(tmp_path, {"ty-111", "hb-HBCAAA"})

    assert len(table) == 3 and table["review_id"].is_unique
    assert report["ty-111"]["reviews"] == 2 and report["ty-111"]["site_total"] == 5
    assert report["ty-111"]["missing"] == 3
    assert report["hb-HBCAAA"]["missing_pages"] == [2]


def test_import_folder_rejects_a_product_outside_the_list(tmp_path):
    write(tmp_path, "t.html", ty_page([ty_review(1, "Sessiz")]))
    with pytest.raises(ValueError, match="t.html"):
        import_folder(tmp_path, {"ty-999"})


def test_import_folder_rejects_an_empty_folder(tmp_path):
    with pytest.raises(ValueError, match="html"):
        import_folder(tmp_path, {"ty-111"})
