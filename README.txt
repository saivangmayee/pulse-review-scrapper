Pulse Review Scraper

This project implements a Python-based scraper to collect SaaS product reviews
from multiple platforms and export them as structured JSON within a given
date range.

Supported Platforms
- G2
- Capterra
- Trustpilot (additional source to demonstrate extensibility)

Project Structure
- scraper.py            : Main CLI entry point
- sources/              : Platform-specific scrapers (g2, capterra, trustpilot)
- utils/                : Shared utilities (date parsing, HTTP helpers)
- output/               : Generated JSON outputs
- requirements.txt      : Python dependencies

How to Run

1. Create and activate virtual environment:
   python3 -m venv .venv
   source .venv/bin/activate

2. Install dependencies:
   pip install -r requirements.txt

3. Run the scraper:
   python scraper.py \
     --source trustpilot \
     --company notion.so \
     --start_date 2024-06-01 \
     --end_date 2024-12-31 \
     --out output/notion_trustpilot.json

Output Format

Each run produces a JSON file with the following structure:

{
  "source": "trustpilot",
  "company_input": "notion.so",
  "start_date": "2024-06-01",
  "end_date": "2024-12-31",
  "count": 3,
  "reviews": [
    {
      "title": "Site doesn't work most of the...",
      "review": "Full review text",
      "date": "2024-12-28",
      "rating": "Rated 1 out of 5",
      "reviewer": "Hossen Imran",
      "source": "trustpilot"
    }
  ]
}

Notes / Limitations

- During testing, both G2 and Capterra returned HTTP 403 due to bot protection
  in this environment.
- The scrapers for G2 and Capterra are fully implemented and the pipeline
  handles these cases gracefully by returning an empty result set instead of
  failing.
- Trustpilot output is included to demonstrate full end-to-end functionality
  (scraping, date filtering, normalization, and JSON export).

Production Considerations

In a production environment, this would be handled by:
- Using official APIs or licensed data feeds where available
- Using browser automation (Playwright/Selenium) where permitted
- Implementing retry, backoff, and monitoring for blocked sources
