import json
import csv
import time
import re
from pathlib import Path
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    )
}

LISTING_URL = "https://www.olx.com.br/imoveis/estado-pb/paraiba/joao-pessoa"

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


def fetch(url: str) -> str:
    """Fetch a given URL and return the text content."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_listing(html: str) -> List[str]:
    """Parse a listing page and return a list of property links."""
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select("a[data-lurker-detail='title']"):
        href = a.get("href")
        if href and href.startswith("http"):
            links.append(href.split("?")[0])
    return list(dict.fromkeys(links))


def parse_property(html: str, url: str) -> Dict[str, str]:
    """Extract property data from an ad page."""
    soup = BeautifulSoup(html, "html.parser")
    data = {"url": url}

    # Try to load structured data if present
    script = soup.find("script", type="application/ld+json")
    if script:
        try:
            json_data = json.loads(script.string)
            if isinstance(json_data, dict):
                data.update(json_data)
        except Exception:
            pass

    # Title and price fallbacks
    title = soup.select_one("h1")
    price = soup.select_one("h2")
    if title:
        data.setdefault("title", title.get_text(strip=True))
    if price:
        # Remove currency symbols and non digits
        raw = price.get_text(strip=True)
        clean = re.sub(r"[^0-9]", "", raw)
        data.setdefault("price", clean)

    # Location info if available
    loc = soup.select_one("span.sc-ge2uzh-0")
    if loc:
        data.setdefault("location", loc.get_text(strip=True))

    desc = soup.select_one("div.sc-1sj73kh-0")
    if desc:
        data.setdefault("description", desc.get_text(" ", strip=True))

    return data


def scrape_all(max_pages: int = 5, delay: float = 1.0) -> List[Dict[str, str]]:
    """Scrape multiple listing pages."""
    results = []
    for page in range(1, max_pages + 1):
        page_url = LISTING_URL if page == 1 else f"{LISTING_URL}?o={page}"
        try:
            html = fetch(page_url)
        except Exception as e:
            print(f"Failed to fetch listing page {page}: {e}")
            break
        for link in parse_listing(html):
            try:
                ad_html = fetch(link)
                data = parse_property(ad_html, link)
                results.append(data)
                time.sleep(delay)
            except Exception as e:
                print(f"Failed to scrape {link}: {e}")
        # Break if there are no next page links
        if f"?o={page+1}" not in html:
            break
    return results


def save_data(items: List[Dict[str, str]], basename: str = "olx_properties") -> None:
    json_path = OUTPUT_DIR / f"{basename}.json"
    csv_path = OUTPUT_DIR / f"{basename}.csv"

    with json_path.open("w", encoding="utf-8") as jf:
        json.dump(items, jf, ensure_ascii=False, indent=2)

    if items:
        keys = sorted({k for item in items for k in item.keys()})
        with csv_path.open("w", newline="", encoding="utf-8") as cf:
            writer = csv.DictWriter(cf, fieldnames=keys)
            writer.writeheader()
            for item in items:
                writer.writerow(item)


if __name__ == "__main__":
    ads = scrape_all()
    save_data(ads)
    print(f"Saved {len(ads)} ads to {OUTPUT_DIR}")
