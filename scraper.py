from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path

from sources.g2 import scrape_g2
from sources.capterra import scrape_capterra
from sources.trustpilot import scrape_trustpilot


def parse_args():
    p = argparse.ArgumentParser(
        description="Scrape SaaS reviews from G2, Capterra, or Trustpilot into JSON."
    )
    p.add_argument("--company", required=True)
    p.add_argument("--source", required=True, choices=["g2", "capterra", "trustpilot"])
    p.add_argument("--start_date", required=True)
    p.add_argument("--end_date", required=True)
    p.add_argument("--out", default="output/reviews.json")
    p.add_argument("--max_pages", type=int, default=50)
    return p.parse_args()


def main():
    args = parse_args()
    print(f"[INFO] Starting scraper: source={args.source}, company={args.company}", flush=True)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Output path: {out_path}", flush=True)

    try:
        if args.source == "g2":
            reviews = scrape_g2(args.company, args.start_date, args.end_date, max_pages=args.max_pages)
        elif args.source == "capterra":
            reviews = scrape_capterra(args.company, args.start_date, args.end_date, max_pages=args.max_pages)
        else:
            reviews = scrape_trustpilot(args.company, args.start_date, args.end_date, max_pages=min(args.max_pages, 30))

        payload = {
            "source": args.source,
            "company_input": args.company,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "count": len(reviews),
            "reviews": reviews,
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        print(f"[DONE] Wrote {len(reviews)} reviews to {out_path}", flush=True)

    except Exception as e:
        print("[ERROR] Script failed with exception:", flush=True)
        print(str(e), flush=True)
        print(traceback.format_exc(), flush=True)
        # still write an error output so you have something in /output
        error_payload = {
            "source": args.source,
            "company_input": args.company,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "count": 0,
            "reviews": [],
            "error": str(e),
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(error_payload, f, ensure_ascii=False, indent=2)
        print(f"[DONE-WITH-ERROR] Wrote error payload to {out_path}", flush=True)


if __name__ == "__main__":
    main()
