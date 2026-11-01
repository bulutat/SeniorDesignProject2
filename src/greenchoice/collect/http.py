"""Kibar (polite) HTTP istemcisi: robots.txt kontrolü, istekler arası bekleme, disk önbelleği.

Akademik amaçlı, düşük hızlı veri toplama içindir. Aynı URL ikinci kez indirilmez. robots.txt
okunamazsa (403, 429, 5xx, ağ hatası) hiçbir adres indirilmez. Kimlik taklidi veya engel aşma yok.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from urllib.parse import urlparse

from greenchoice.collect.robots import Robots, robots_from_response
from greenchoice.config import RAW_DIR

USER_AGENT = "GreenChoice-AcademicResearch/0.1 (bitirme projesi; dusuk hizli toplama)"


class PoliteClient:
    def __init__(self, min_delay_s: float = 2.0, cache_dir: Path | None = None,
                 respect_robots: bool = True, timeout_s: float = 20.0, session=None):
        if session is None:
            import requests  # scrape extra'sı: pip install -e ".[scrape]"
            session = requests.Session()
        self.session = session
        self.session.headers["User-Agent"] = USER_AGENT
        self.min_delay_s = min_delay_s
        self.timeout_s = timeout_s
        self.cache_dir = cache_dir or RAW_DIR / "http_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.respect_robots = respect_robots
        self._robots: dict[str, Robots] = {}
        self._last_request = 0.0

    def _wait_turn(self) -> None:
        wait = self.min_delay_s - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)

    def _robots_for(self, base: str) -> Robots:
        if base not in self._robots:
            self._wait_turn()
            try:
                resp = self.session.get(f"{base}/robots.txt", timeout=self.timeout_s)
                self._robots[base] = robots_from_response(resp.status_code, resp.text, USER_AGENT)
            except OSError:  # requests' exceptions derive from OSError: unreadable means closed
                self._robots[base] = Robots.disallow_all()
            self._last_request = time.monotonic()
        return self._robots[base]

    def _allowed(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parts = urlparse(url)
        path = parts.path + (f"?{parts.query}" if parts.query else "")
        return self._robots_for(f"{parts.scheme}://{parts.netloc}").allowed(path)

    def _cache_file(self, url: str) -> Path:
        return self.cache_dir / (hashlib.sha1(url.encode()).hexdigest() + ".txt")

    def get_text(self, url: str, **kwargs) -> str:
        cached = self._cache_file(url)
        if cached.exists():
            return cached.read_text(encoding="utf-8")
        if not self._allowed(url):
            raise PermissionError(f"robots.txt bu adrese izin vermiyor: {url}")

        self._wait_turn()
        resp = self.session.get(url, timeout=self.timeout_s, **kwargs)
        self._last_request = time.monotonic()
        resp.raise_for_status()
        cached.write_text(resp.text, encoding="utf-8")
        return resp.text
