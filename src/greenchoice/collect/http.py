"""Kibar (polite) HTTP istemcisi: robots.txt kontrolü, istekler arası bekleme, disk önbelleği.

Akademik amaçlı, düşük hızlı veri toplama içindir. Aynı URL ikinci kez indirilmez.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlparse

from greenchoice.config import RAW_DIR

USER_AGENT = "GreenChoice-AcademicResearch/0.1 (bitirme projesi; dusuk hizli toplama)"


class PoliteClient:
    def __init__(self, min_delay_s: float = 2.0, cache_dir: Path | None = None,
                 respect_robots: bool = True, timeout_s: float = 20.0):
        import requests  # scrape extra'sı: pip install -e ".[scrape]"

        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.min_delay_s = min_delay_s
        self.timeout_s = timeout_s
        self.cache_dir = cache_dir or RAW_DIR / "http_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.respect_robots = respect_robots
        self._robots: dict[str, robotparser.RobotFileParser] = {}
        self._last_request = 0.0

    def _allowed(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parts = urlparse(url)
        base = f"{parts.scheme}://{parts.netloc}"
        if base not in self._robots:
            rp = robotparser.RobotFileParser(f"{base}/robots.txt")
            try:
                rp.read()
            except OSError:
                pass
            self._robots[base] = rp
        return self._robots[base].can_fetch(USER_AGENT, url)

    def _cache_file(self, url: str) -> Path:
        return self.cache_dir / (hashlib.sha1(url.encode()).hexdigest() + ".txt")

    def get_text(self, url: str, **kwargs) -> str:
        cached = self._cache_file(url)
        if cached.exists():
            return cached.read_text(encoding="utf-8")
        if not self._allowed(url):
            raise PermissionError(f"robots.txt bu adrese izin vermiyor: {url}")

        wait = self.min_delay_s - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        resp = self.session.get(url, timeout=self.timeout_s, **kwargs)
        self._last_request = time.monotonic()
        resp.raise_for_status()
        cached.write_text(resp.text, encoding="utf-8")
        return resp.text
