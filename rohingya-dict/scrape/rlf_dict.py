"""
Scrape the Rohingya-to-English dictionary from rohingyalanguage.com.

The dictionary is split across 26 pages (a.htm - z.htm).
Pages a.htm and b.htm use an HTML table with two columns.
Pages c.htm - z.htm use inline text: word (definition)<br>.

Outputs: output/raw_rlf.json
"""

import json
import re
import string
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = (
    "https://www.rohingyalanguage.com"
    "/rohingya-english-dictionary-v0/rohingya_dictionary/{letter}.htm"
)
OUTPUT = Path(__file__).resolve().parent.parent / "output" / "raw_rlf.json"

SKIP_WORDS = {
    "homepage", "rohingya words", "rohingya", "go top", "back to top",
    "rohingya to english", "language of rohingyas",
}


def fetch_page(url: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            resp.encoding = "latin-1"
            return resp.text
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                raise


def parse_table_page(html: str) -> list[dict]:
    """Parse pages that use <tr>/<td> table structure (a.htm, b.htm)."""
    soup = BeautifulSoup(html, "lxml")
    entries = []

    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        rohingya = cells[0].get_text(strip=True)
        english = cells[1].get_text(strip=True)

        if not rohingya or not english:
            continue
        if rohingya.lower() in SKIP_WORDS:
            continue
        if "dictionary" in rohingya.lower() or "dictionary" in english.lower():
            continue
        if english.lower().startswith("meaning in"):
            continue
        if "last update" in english.lower():
            continue
        if re.match(r"^about \d+ words", english.lower()):
            continue
        if rohingya in ("A", "B") and "dictionary" in english.lower():
            continue

        entries.append({
            "rohingya": rohingya,
            "english": english,
        })

    return entries


def parse_inline_page(html: str) -> list[dict]:
    """Parse pages that use inline word (definition) format (c.htm - z.htm).

    Strategy: collapse all whitespace in the extracted text, then find all
    occurrences of a word token followed by (definition in parens).
    """
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ")
    text = re.sub(r"[\s\xa0]+", " ", text).strip()

    WORD = r"[A-Za-z\u00C0-\u024F\u0300-\u036F']+"
    WORD_MAYBE_SPACE = r"[A-Za-z\u00C0-\u024F\u0300-\u036F' -]+"

    entry_re = re.compile(
        r"(?:^|\s)"
        r"(" + WORD + r"(?:\s+" + WORD + r")*?)"
        r"\s+"
        r"\(([^)]+)\)"
    )

    entries = []
    for m in entry_re.finditer(text):
        rohingya = m.group(1).strip()
        english = m.group(2).strip()

        if not rohingya or not english:
            continue
        if rohingya.lower() in SKIP_WORDS:
            continue
        if len(rohingya) > 60:
            continue
        if re.match(r"^(About|Updated|Last|Go|Back)", rohingya):
            continue
        if "dictionary" in rohingya.lower():
            continue

        entries.append({"rohingya": rohingya, "english": english})

    return entries


def parse_letter_page(html: str, letter: str) -> list[dict]:
    if letter in ("a", "b"):
        entries = parse_table_page(html)
        if entries:
            return entries
    return parse_inline_page(html)


def main():
    all_entries = []
    letters = list(string.ascii_lowercase)

    for letter in letters:
        url = BASE_URL.format(letter=letter)
        print(f"  Fetching {letter}.htm ...", end=" ", flush=True)
        try:
            html = fetch_page(url)
            entries = parse_letter_page(html, letter)
            all_entries.extend(entries)
            print(f"{len(entries)} entries")
        except Exception as e:
            print(f"FAILED: {e}")
        time.sleep(0.5)

    print(f"\nTotal: {len(all_entries):,} entries")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print(f"Written to {OUTPUT}")

    if all_entries:
        print("\nSample entries:")
        for e in all_entries[:5]:
            print(f"  {e['rohingya']}: {e['english'][:80]}")
        print("  ...")
        for e in all_entries[-3:]:
            print(f"  {e['rohingya']}: {e['english'][:80]}")


if __name__ == "__main__":
    main()
