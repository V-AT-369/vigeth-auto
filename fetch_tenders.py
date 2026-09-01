#!/usr/bin/env python3
"""
Vigeth Tenders — IT/software services tender fetcher (v1.1)

What this does:
  Pulls recent tender notices from official, free, open government procurement
  APIs and filters them down to IT/software services (CPV division 72), then
  writes a plain digest file you can turn into content.

Status of each source in this version:
  - UK Find a Tender Service: fully implemented (official OCDS API, no key needed).
  - Australia AusTender: stubbed — needs the exact current API base URL confirmed
    against https://github.com/austender/austender-ocds-api before it will work.
  - EU TED: not yet implemented (its open-data format is more involved — XML/
    eForms based) — planned for a follow-up version.

Usage:
  pip install requests
  python -u fetch_tenders.py
  (writes tenders_digest.md and tenders_raw.json next to this script)
"""
import json
import sys
import time
from datetime import datetime, timedelta, timezone

print("Vigeth tender fetcher starting...", flush=True)

try:
    import requests
except ImportError:
    print("Missing dependency. Run: pip install requests", flush=True)
    sys.exit(1)

IT_CPV_PREFIX = "72"  # CPV division 72 = IT services: consulting, software dev, internet, support


def fetch_uk_find_a_tender(days_back=14, limit=100):
    """Official UK Find a Tender OCDS API. No API key required.
    Docs: https://www.find-tender.service.gov.uk/Developer/Documentation
    """
    base = "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages"
    updated_to = datetime.now(timezone.utc)
    updated_from = updated_to - timedelta(days=days_back)
    params = {
        "updatedFrom": updated_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updatedTo": updated_to.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": limit,
    }
    results = []
    cursor = None
    page = 0
    while True:
        if cursor:
            params["cursor"] = cursor
        print(f"  UK: requesting page {page}...", flush=True)
        resp = requests.get(base, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        releases = data.get("releases", [])
        print(f"  UK: page {page} returned {len(releases)} releases", flush=True)
        for r in releases:
            tender = r.get("tender", {}) or {}
            items = tender.get("items", []) or []
            is_it = any(
                (it.get("classification", {}) or {}).get("id", "").startswith(IT_CPV_PREFIX)
                for it in items
            )
            if not is_it:
                continue
            buyer_name = (r.get("buyer", {}) or {}).get("name", "Unknown buyer")
            value = (tender.get("value", {}) or {})
            results.append({
                "source": "UK Find a Tender",
                "title": tender.get("title", "(no title)"),
                "buyer": buyer_name,
                "deadline": (tender.get("tenderPeriod", {}) or {}).get("endDate"),
                "value_amount": value.get("amount"),
                "value_currency": value.get("currency"),
                "url": r.get("uri") or "",
            })
        cursor = data.get("links", {}).get("next")
        page += 1
        if not cursor or not releases or page > 20:
            break
    return results


def fetch_austender_stub():
    """Placeholder — confirm the live API base URL and auth requirements against
    https://github.com/austender/austender-ocds-api before implementing.
    """
    return []


def main():
    all_results = []
    try:
        uk_results = fetch_uk_find_a_tender()
        all_results.extend(uk_results)
        print(f"UK Find a Tender: {len(uk_results)} IT/software matches", flush=True)
    except Exception as e:
        print(f"UK Find a Tender fetch failed: {type(e).__name__}: {e}", flush=True)

    au_results = fetch_austender_stub()
    all_results.extend(au_results)

    with open("tenders_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    with open("tenders_digest.md", "w", encoding="utf-8") as f:
        f.write(f"# Vigeth Tenders — IT/Software Services Digest\n")
        f.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n")
        if not all_results:
            f.write("No matching tenders found in this run.\n")
        for r in all_results:
            f.write(f"## {r['title']}\n")
            f.write(f"- Source: {r['source']}\n")
            f.write(f"- Buyer: {r['buyer']}\n")
            f.write(f"- Deadline: {r.get('deadline', 'n/a')}\n")
            value = r.get("value_amount")
            if value:
                f.write(f"- Estimated value: {value} {r.get('value_currency', '')}\n")
            if r.get("url"):
                f.write(f"- Link: {r['url']}\n")
            f.write("\n")

    print(f"Wrote {len(all_results)} results to tenders_digest.md and tenders_raw.json", flush=True)
    sys.stdout.flush()
    time.sleep(3)  # give the log collector time to ship output before the container exits


if __name__ == "__main__":
    main()
