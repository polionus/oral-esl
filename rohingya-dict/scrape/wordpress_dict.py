"""
Parse the English-Rohingya dictionary from rohingyadictionary.wordpress.com.

The full dictionary text is stored locally in scrape/wordpress_raw_page.txt
(the live WordPress page truncates after ~500 entries).

Entry format in the text:
  .englishWord<>rohingyaTranslation1 (pos.) , rohingyaTranslation2 (pos.)

Outputs: output/raw_wordpress.json
"""

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_FILE = SCRIPT_DIR / "wordpress_raw_page.txt"
OUTPUT = SCRIPT_DIR.parent / "output" / "raw_wordpress.json"

POS_PATTERN = re.compile(r"\(([^)]+)\)\s*$")
ENTRY_PATTERN = re.compile(r"\.([\w][^<]*?)<>(.*?)(?=\.[a-zA-Z]|$)")


def load_text() -> str:
    if not LOCAL_FILE.exists():
        raise FileNotFoundError(
            f"Source file not found: {LOCAL_FILE}\n"
            "Place the full dictionary text in scrape/wordpress_raw_page.txt"
        )
    return LOCAL_FILE.read_text(encoding="utf-8")


def extract_entries(text: str) -> list[dict]:
    start = text.find(".a<>")
    if start == -1:
        start = text.find(".a ")
    if start > 0:
        text = text[start:]

    blob = " ".join(text.splitlines())
    matches = ENTRY_PATTERN.findall(blob)

    entries = []
    seen = set()
    for eng_raw, rhg_raw in matches:
        english = eng_raw.strip().lower()
        english = re.sub(r"\d+$", "", english).strip()
        if not english:
            continue
        if any(c in english for c in ["http", "://", "[", "]", "<", ">"]):
            continue
        if len(english) > 80:
            continue

        translations = parse_translations(rhg_raw.strip())
        if not translations:
            continue

        key = english
        if key in seen:
            for existing in entries:
                if existing["english"] == english:
                    existing_texts = {t["text"] for t in existing["translations"]}
                    for t in translations:
                        if t["text"] not in existing_texts:
                            existing["translations"].append(t)
                    break
        else:
            seen.add(key)
            entries.append({
                "english": english,
                "translations": translations,
            })

    return entries


def parse_translations(raw: str) -> list[dict]:
    parts = re.split(r"\s*,\s*(?=[a-zA-ZáéíóúàèìòùãõñçÁÉÍÓÚÀÈÌÒÙÃÕÑÇ])", raw)
    results = []
    for part in parts:
        part = part.strip()
        if not part:
            continue

        pos_match = POS_PATTERN.search(part)
        pos = ""
        text = part
        if pos_match:
            pos = pos_match.group(1).strip().rstrip(".")
            text = part[: pos_match.start()].strip()

        text = text.strip(" ,.")
        if not text:
            continue

        results.append({"text": text, "pos": pos})

    return results


def main():
    print(f"Loading {LOCAL_FILE} ...")
    text = load_text()
    print(f"  Loaded {len(text):,} characters")

    entries = extract_entries(text)
    print(f"  Parsed {len(entries):,} unique entries")

    pos_counts: dict[str, int] = {}
    for e in entries:
        for t in e["translations"]:
            p = t["pos"] or "unknown"
            pos_counts[p] = pos_counts.get(p, 0) + 1
    print(f"  POS distribution: {dict(sorted(pos_counts.items(), key=lambda x: -x[1])[:10])}")

    letter_counts: dict[str, int] = {}
    for e in entries:
        first = e["english"][0] if e["english"] else "?"
        letter_counts[first] = letter_counts.get(first, 0) + 1
    print(f"  Letter coverage: {dict(sorted(letter_counts.items()))}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"  Written to {OUTPUT}")

    if entries:
        print("\nSample entries:")
        for e in entries[:5]:
            print(f"  {e['english']}: {[t['text'] for t in e['translations'][:3]]}")


if __name__ == "__main__":
    main()
