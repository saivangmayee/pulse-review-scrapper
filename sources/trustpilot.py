from __future__ import annotations

from bs4 import BeautifulSoup
from dateutil.parser import parse
import requests

from utils.date_utils import to_date, in_range
from utils.helpers import fetch, polite_sleep


def _safe_text(el) -> str:
    return el.get_text(" ", strip=True) if el else ""


def _extract_rating(article) -> str:
    # 1) aria-label: "Rated X out of 5"
    r1 = article.find(attrs={"aria-label": lambda x: x and "rated" in x.lower()})
    if r1 and r1.get("aria-label"):
        return r1["aria-label"].strip()

    # 2) data attribute
    r2 = article.find(attrs={"data-service-review-rating": True})
    if r2:
        val = r2.get("data-service-review-rating", "")
        return val.strip()

    # 3) schema/meta
    r3 = article.find("meta", attrs={"itemprop": "ratingValue"})
    if r3 and r3.get("content"):
        return str(r3["content"]).strip()

    return ""


def _extract_reviewer(article) -> str:
    """
    Try Trustpilot's consumer name attribute first; fallback to common 'consumer' class.
    """
    el = article.find(["span", "div"], attrs={"data-consumer-name-typography": True})
    if el:
        return _safe_text(el)

    el2 = article.find(["span", "div"], class_=lambda cl: cl and "consumer" in cl.lower())
    return _safe_text(el2)


def _extract_title(article) -> str:
    # Sometimes title is in h2/h3; sometimes missing
    return _safe_text(article.find(["h2", "h3"]))


def _extract_body(article) -> str:
    # Usually first paragraph is body; sometimes multiple paragraphs exist
    p = article.find("p")
    if p:
        return _safe_text(p)
    return ""


def scrape_trustpilot(domain_or_slug: str, start_date: str, end_date: str, max_pages: int = 30) -> list[dict]:
    start = to_date(start_date)
    end = to_date(end_date)

    session = requests.Session()
    out: list[dict] = []

    base_url = f"https://www.trustpilot.com/review/{domain_or_slug}"

    for page in range(1, max_pages + 1):
        url = base_url if page == 1 else f"{base_url}?page={page}"

        try:
            html = fetch(url, session=session)
        except Exception:
            break

        soup = BeautifulSoup(html, "lxml")
        cards = soup.find_all("article")
        if not cards:
            break

        page_reviews: list[dict] = []
        for c in cards:
            # date: time tag datetime
            t = c.find("time")
            if not (t and t.get("datetime")):
                continue
            try:
                dt = parse(t["datetime"]).date()
            except Exception:
                continue

            
            body = _extract_body(c) or ""
            title = _extract_title(c)
            if not title:
                words = body.split()
                title = " ".join(words[:6]) + ("..." if len(words) > 6 else "")
            rating = _extract_rating(c)
            reviewer = _extract_reviewer(c)

            page_reviews.append(
                {
                    "title": title,
                    "review": body,
                    "date": str(dt),
                    "rating": rating,
                    "reviewer": reviewer,
                    "source": "trustpilot",
                }
            )

        if not page_reviews:
            break

        # Filter by date range and early-stop when older than start_date
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
