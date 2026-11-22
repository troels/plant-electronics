#!/usr/bin/env python3
"""Look up parts with Mouser's Search API and print price and stock.

Usage:  python3 tools/mouser.py PART [PART ...]
        python3 tools/mouser.py --keyword "words to search"

The API key is read from the MOUSER_API_KEY environment variable or from
a .env file in the repository root. It is never printed. Mouser's API
takes the key as a URL parameter, so it travels in the request URL (over
HTTPS) to api.mouser.com and nowhere else.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.mouser.com/api/v1/search/"


def api_key():
    key = os.environ.get("MOUSER_API_KEY")
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("MOUSER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip("\"'")
    if not key:
        sys.exit("No MOUSER_API_KEY in the environment or in .env")
    return key


def call(endpoint, body, key):
    req = urllib.request.Request(API + endpoint + "?apiKey=" + key,
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:      # never echo the URL: it holds the key
        return {"Errors": [{"Message": f"HTTP {e.code} {e.reason}"}]}
    except urllib.error.URLError as e:
        return {"Errors": [{"Message": f"network error: {e.reason}"}]}


def rows(result, limit):
    if result.get("Errors"):
        yield "  error: " + "; ".join(str(e.get("Message")) for e in result["Errors"])
        return
    parts = (result.get("SearchResults") or {}).get("Parts") or []
    if not parts:
        yield "  no match"
    for p in parts[:limit]:
        breaks = p.get("PriceBreaks") or []
        price = "; ".join(f'{b["Quantity"]}+ {b["Price"]}' for b in breaks[:3]) or "no price"
        url = (p.get("ProductDetailUrl") or "").split("?")[0]
        stock = p.get("AvailabilityInStock")
        stock = f"{stock} in stock" if stock not in (None, "") else (p.get("Availability") or "stock not given")
        yield (f'  {p.get("ManufacturerPartNumber")} | {p.get("Manufacturer")} | '
               f'{stock}, lead {p.get("LeadTime") or "?"} | {price} | '
               f'{(p.get("Description") or "")[:60]} | {url}')


def main(argv):
    keyword = argv and argv[0] == "--keyword"
    terms = argv[1:] if keyword else argv
    if not terms:
        sys.exit(__doc__)
    key = api_key()
    for i, term in enumerate(terms):
        if i:
            time.sleep(2.2)                   # stay under Mouser's calls-per-minute limit
        if keyword:
            body = {"SearchByKeywordRequest": {"keyword": term, "records": 8, "startingRecord": 0}}
            result = call("keyword", body, key)
        else:
            body = {"SearchByPartRequest": {"mouserPartNumber": term, "partSearchOptions": "BeginsWith"}}
            result = call("partnumber", body, key)
        print(term)
        for row in rows(result, 4 if keyword else 3):
            print(row)


if __name__ == "__main__":
    main(sys.argv[1:])
