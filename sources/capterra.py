from __future__ import annotations

import re
from bs4 import BeautifulSoup
from dateutil.parser import parse
import requests

from utils.date_utils import to_date, in_range
from utils.helpers import fetch, polite_sleep


def _safe_text(el) -> str:
    return el.get_text(" ", strip=True) if el else ""


def _parse_reviews(soup: BeautifulSoup) -> list[dict]:
    reviews: list[dict] = []

    cards = soup.find_all(["article", "div"], attrs={"data-testid": lambda x: x and "review" in x.lower()})
    if not cards:
        cards = soup.find_all("div", class_=lambda c: c and "review" in c.lower())

    for c in cards:
        dt = None

        t = c.find("time")
        if t and t.get("datetime"):
            try:
                dt = parse(t["datetime"]).date()
            except Exception:
                dt = None

        if not dt:
            # fallback: try parsing any date-looking text
            text = c.get_text(" ", strip=True)
            for token in re.split(r"\||\n", text):
                try:
                    dt = parse(token, fuzzy=True).date()
                    break
                except Exception:
                    continue

        title = _safe_text(c.find(["h3", "h2"]))
        body = _safe_text(c.find("p"))

        rating = ""
        # sometimes rating is in aria-label
        r_el = c.find(attrs={"aria-label": lambda x: x and ("rating" in x.lower() or "star" in x.lower())})
        if r_el:
            rating = r_el.get("aria-label", "")
        if not rating:
            r2 = c.find("span", class_=lambda cl: cl and "rating" in cl.lower())
            rating = _safe_text(r2)

        reviewer = ""
        rv = c.find(["span", "div"], class_=lambda cl: cl and ("reviewer" in cl.lower() or "user" in cl.lower() or "name" in cl.lower()))
        reviewer = _safe_text(rv)

        if dt and (title or body):
            reviews.append(
                {
                    "title": title or "(no title)",
                    "review": body or "",
                    "date": str(dt),
                    "rating": rating,
                    "reviewer": reviewer,
                    "source": "capterra",
                }
            )

    return reviews


def scrape_capterra(product_url: str, start_date: str, end_date: str, max_pages: int = 50) -> list[dict]:
    start = to_date(start_date)
    end = to_date(end_date)

    session = requests.Session()
    out: list[dict] = []

    base = product_url.rstrip("/")
    if not base.endswith("reviews"):
        base = base + "/reviews"
    base = base + "/"

    for page in range(1, max_pages + 1):
        url = base if page == 1 else f"{base}?page={page}"

        try:
            html = fetch(url, session=session)
        except Exception:
            break

        soup = BeautifulSoup(html, "lxml")
        page_reviews = _parse_reviews(soup)

        if not page_reviews:
            break

        inrange: list[dict] = []
        oldest = None

        for r in page_reviews:
            d = parse(r["date"]).date()
            oldest = d if oldest is None else min(oldest, d)
            if in_range(d, start, end):
                inrange.append(r)

        out.extend(inrange)

        if oldest and oldest < start:
            break

        polite_sleep()

    return out
