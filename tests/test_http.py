import pytest
import requests

from greenchoice.collect import http
from greenchoice.collect.http import USER_AGENT, PoliteClient

SHOP = "https://shop.example"


class FakeResponse:
    def __init__(self, status, text=""):
        self.status_code, self.text = status, text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    """Serves canned responses and records every request. No network."""

    def __init__(self, pages):
        self.pages, self.calls, self.headers = pages, [], {}

    def get(self, url, timeout=None, **kwargs):
        self.calls.append(url)
        return self.pages.get(url, FakeResponse(404))


def client(tmp_path, pages, **kwargs):
    session = FakeSession(pages)
    kwargs.setdefault("min_delay_s", 0)
    return PoliteClient(cache_dir=tmp_path, session=session, **kwargs), session


ROBOTS = f"{SHOP}/robots.txt"


def test_allowed_page_is_fetched_with_the_honest_user_agent(tmp_path):
    c, s = client(tmp_path, {ROBOTS: FakeResponse(200, "User-agent: *\nDisallow: /sr?\n"),
                             f"{SHOP}/a-p-1": FakeResponse(200, "hello")})
    assert c.get_text(f"{SHOP}/a-p-1") == "hello"
    assert s.calls == [ROBOTS, f"{SHOP}/a-p-1"]
    assert s.headers["User-Agent"] == USER_AGENT


def test_disallowed_page_is_never_requested(tmp_path):
    c, s = client(tmp_path, {ROBOTS: FakeResponse(200, "User-agent: *\nDisallow: /*?q=\n")})
    with pytest.raises(PermissionError, match="robots.txt"):
        c.get_text(f"{SHOP}/anything-p-1?q=x")
    assert s.calls == [ROBOTS]


@pytest.mark.parametrize("status", [403, 500])
def test_unreadable_robots_means_nothing_is_fetched(tmp_path, status):
    c, s = client(tmp_path, {ROBOTS: FakeResponse(status, "captcha")})
    with pytest.raises(PermissionError):
        c.get_text(f"{SHOP}/a-p-1")
    assert s.calls == [ROBOTS]


def test_missing_robots_file_allows_fetching(tmp_path):
    c, _ = client(tmp_path, {f"{SHOP}/a-p-1": FakeResponse(200, "ok")})  # robots.txt -> 404
    assert c.get_text(f"{SHOP}/a-p-1") == "ok"


def test_robots_and_pages_are_cached(tmp_path):
    c, s = client(tmp_path, {ROBOTS: FakeResponse(200, ""), f"{SHOP}/a-p-1": FakeResponse(200, "x"),
                             f"{SHOP}/b-p-2": FakeResponse(200, "y")})
    c.get_text(f"{SHOP}/a-p-1")
    c.get_text(f"{SHOP}/a-p-1")
    c.get_text(f"{SHOP}/b-p-2")
    assert s.calls.count(ROBOTS) == 1
    assert s.calls.count(f"{SHOP}/a-p-1") == 1


def test_requests_are_spaced_by_the_minimum_delay(tmp_path, monkeypatch):
    slept = []
    monkeypatch.setattr(http.time, "sleep", slept.append)
    c, _ = client(tmp_path, {ROBOTS: FakeResponse(200, ""), f"{SHOP}/a-p-1": FakeResponse(200, "x"),
                             f"{SHOP}/b-p-2": FakeResponse(200, "y")}, min_delay_s=2.0)
    c.get_text(f"{SHOP}/a-p-1")
    c.get_text(f"{SHOP}/b-p-2")
    assert slept and all(0 < s <= 2.0 for s in slept)


def test_http_errors_are_not_cached(tmp_path):
    c, s = client(tmp_path, {ROBOTS: FakeResponse(200, ""), f"{SHOP}/a-p-1": FakeResponse(500)})
    with pytest.raises(requests.HTTPError):
        c.get_text(f"{SHOP}/a-p-1")
    s.pages[f"{SHOP}/a-p-1"] = FakeResponse(200, "recovered")
    assert c.get_text(f"{SHOP}/a-p-1") == "recovered"
