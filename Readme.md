Pulse Review Scraper

Pulse Review Scraper is a Python-based CLI tool that collects SaaS product reviews from multiple platforms and exports them as structured JSON within a specified date range.

The project is designed to be extensible, fault-tolerant, and production-aware, gracefully handling blocked sources while maintaining a consistent output format.

Supported Platforms

G2

Capterra

Trustpilot (included to demonstrate full end-to-end functionality)

Project Structure
scraper.py            # Main CLI entry point
sources/              # Platform-specific scrapers (g2, capterra, trustpilot)
utils/                # Shared utilities (date parsing, HTTP helpers)
output/               # Generated JSON outputs
requirements.txt      # Python dependencies

How to Run
1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

2. Install dependencies
pip install -r requirements.txt

3. Run the scraper
python scraper.py \
  --source trustpilot \
  --company notion.so \
  --start_date 2024-06-01 \
  --end_date 2024-12-31 \
  --out output/notion_trustpilot.json

CLI Arguments
Argument	Description
--source	Review source (g2, capterra, trustpilot)
--company	Company name or domain
--start_date	Start date (YYYY-MM-DD)
--end_date	End date (YYYY-MM-DD)
--out	Output JSON file path
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

During testing, both G2 and Capterra returned HTTP 403 errors due to bot protection.

Scrapers for G2 and Capterra are fully implemented, and the pipeline handles these cases gracefully by returning an empty result set instead of failing.

Trustpilot output is included to demonstrate full end-to-end functionality:

scraping

date filtering

normalization

JSON export

Production Considerations

In a production environment, this would be handled by:

Using official APIs or licensed data feeds where available

Using browser automation (Playwright or Selenium) where permitted

Implementing retries, exponential backoff, and monitoring for blocked sources

Extensibility

New platforms can be added by:

Creating a new scraper module under sources/

Implementing the common review schema

Registering the source in scraper.py
