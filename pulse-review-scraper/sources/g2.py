from __future__ import annotations

from bs4 import BeautifulSoup
from dateutil.parser import parse
from datetime import date
import requests

from utils.date_utils import to_date, in_range
from utils.helpers import fetch, polite_sleep


def _safe_text(el) -> str:
    return el.get_text(" ", strip=True) if el else ""


def _parse_review_blocks(soup: BeautifulSoup) -> list[dict]:
    """
    G2 HTML can change often. We use multiple fallbacks.
    We try to find blocks that look like reviews and contain a <time datetime="..."> tag.
    """
    reviews: list[dict] = []

    # 1) Prefer blocks with a review-ish data-testid
    blocks = soup.find_all(
        ["article", "div"],
        attrs={"data-testid": lambda x: x and "review" in x.lower()},
    )

    # 2) Fallback: any div with class containing 'review'
    if not blocks:
        blocks = soup.find_all("div", class_=lambda c: c and "review" in c.lower())

    # 3) Last fallback: any parent of a <time> tag
    if not blocks:
        blocks = [t.parent for t in soup.find_all("time") if t.parent]

    seen = set()
    for b in blocks:
        t = b.find("time")
        if not (t and t.get("datetime")):
            continue

        try:
            dt = parse(t["datetime"]).date()
        except Exception:
            continue

        title = _safe_text(b.find(["h3", "h2"]))
        body = _safe_text(b.find("p"))

        # rating: sometimes in aria-label like "5 stars"
        rating = ""
        r_el = b.find(attrs={"aria-label": lambda x: x and "star" in x.lower()})
        if r_el:
            rating = r_el.get("aria-label", "")
        if not rating:
            r2 = b.find("span", class_=lambda c: c and "rating" in c.lower())
            rating = _safe_text(r2)

        reviewer = ""
        rv = b.find(["span", "div"], class_=lambda c: c and ("user" in c.lower() or "reviewer" in c.lower()))
        reviewer = _safe_text(rv)

        key = (title, body, str(dt))
        if key in seen:
            continue
        seen.add(key)

        if title or body:
            reviews.append(
                {
                    "title": title or "(no title)",
                    "review": body or "",
                    "date": str(dt),
                    "rating": rating,
                    "reviewer": reviewer,
                    "source": "g2",
                }
            )

    return reviews


def scrape_g2(product_slug: str, start_date: str, end_date: str, max_pages: int = 50) -> list[dict]:
    """
    Scrape G2 reviews for a product slug.

    Example:
      product_slug = "chargebee"
      URL becomes: https://www.g2.com/products/chargebee/reviews?page=1

    Note:
      G2 may sometimes show login gates or partial HTML content.
      If you see count=0, try another product slug or use capterra/trustpilot for demo.
    """
    start = to_date(start_date)
    end = to_date(end_date)

    session = requests.Session()
    out: list[dict] = []

    for page in range(1, max_pages + 1):
        url = f"https://www.g2.com/products/{product_slug}/reviews?page={page}"
        try:
            html = fetch(url, session=session)
        except Exception:
            break

        soup = BeautifulSoup(html, "lxml")
        page_reviews = _parse_review_blocks(soup)

        if not page_reviews:
            break

        inrange: list[dict] = []
        oldest: date | None = None

        for r in page_reviews:
            d = parse(r["date"]).date()
            oldest = d if oldest is None else min(oldest, d)
            if in_range(d, start, end):
                inrange.append(r)

        out.extend(inrange)

        # Early stop if pages are newest-first and we already passed start_date
        if oldest and oldest < start:
            break

        polite_sleep()

    return out
