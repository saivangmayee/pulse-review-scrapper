from __future__ import annotations

import random
import time
import requests


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.google.com/",
}




class FetchError(RuntimeError):
    pass


def fetch(url: str, *, session: requests.Session | None = None, timeout: int = 30) -> str:
    s = session or requests.Session()
    r = s.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    if r.status_code == 403:
        raise FetchError(f"HTTP 403 (blocked by bot protection) for {url}")
    if r.status_code == 429:
        raise FetchError(f"HTTP 429 (rate limited) for {url}")
    if r.status_code >= 400:
        raise FetchError(f"HTTP {r.status_code} for {url}")
    return r.text



def polite_sleep(min_s: float = 0.8, max_s: float = 1.8) -> None:
    """Small random delay to reduce load and rate-limit risk."""
    time.sleep(random.uniform(min_s, max_s))
