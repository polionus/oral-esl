"""
Clean, normalize, and merge the two raw dictionary sources into unified outputs:
  - output/dictionary.json     (unified dictionary)
  - output/rag_corpus.json     (RAG-optimized documents)
  - output/finetune_pairs.jsonl (instruction-tuning pairs)

Reads:
  - output/raw_wordpress.json  (English -> Rohingya, ~6,800 entries)
  - output/raw_rlf.json        (Rohingya -> English, ~5,500 entries)
"""

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_WP = ROOT / "output" / "raw_wordpress.json"
RAW_RLF = ROOT / "output" / "raw_rlf.json"
OUT_DICT = ROOT / "output" / "dictionary.json"
OUT_RAG = ROOT / "output" / "rag_corpus.json"
OUT_FT = ROOT / "output" / "finetune_pairs.jsonl"


def normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_english(s: str) -> str:
    return normalize_text(s).lower().strip(" .")


def normalize_rohingya(s: str) -> str:
    return normalize_text(s).strip(" .")


def load_wordpress() -> list[dict]:
    if not RAW_WP.exists():
        print(f"  WARNING: {RAW_WP} not found, skipping")
        return []
    with open(RAW_WP, encoding="utf-8") as f:
        return json.load(f)


def load_rlf() -> list[dict]:
    if not RAW_RLF.exists():
        print(f"  WARNING: {RAW_RLF} not found, skipping")
        return []
    with open(RAW_RLF, encoding="utf-8") as f:
        return json.load(f)


POS_NORMALIZE = {
    "n": "noun",
    "v": "verb",
    "adj": "adjective",
    "adv": "adverb",
    "prep": "preposition",
    "pron": "pronoun",
    "conj": "conjunction",
    "phrase": "phrase",
    "n. adj": "noun/adjective",
    "adj. bengali": "adjective",
    "adj. bengal": "adjective",
    "adv. adj": "adverb/adjective",
}


def normalize_pos(raw_pos: str) -> str:
    key = raw_pos.lower().strip().rstrip(".")
    return POS_NORMALIZE.get(key, key)


def build_unified_dictionary(wp_data: list[dict], rlf_data: list[dict]) -> list[dict]:
    """Merge both sources into a unified list of dictionary entries."""

    en_to_rhg: dict[str, dict] = {}
    rhg_to_en: dict[str, dict] = {}

    entry_id = 0

    for wp_entry in wp_data:
        english = normalize_english(wp_entry["english"])
        if not english or len(english) > 80:
            continue

        rhg_texts = []
        pos_set = set()
        for t in wp_entry.get("translations", []):
            text = normalize_rohingya(t["text"])
            if text:
                rhg_texts.append(text)
            pos = normalize_pos(t.get("pos", ""))
            if pos:
                pos_set.add(pos)

        if not rhg_texts:
            continue

        entry_id += 1
        entry = {
            "id": f"wp_{entry_id:05d}",
            "english": english,
            "rohingya": rhg_texts,
            "pos": sorted(pos_set) if pos_set else [],
            "definition_en": "",
            "source": ["wordpress"],
        }
        en_to_rhg[english] = entry

    for rlf_entry in rlf_data:
        rohingya = normalize_rohingya(rlf_entry["rohingya"])
        english_def = normalize_text(rlf_entry["english"])

        if not rohingya or not english_def:
            continue
        if len(rohingya) > 60:
            continue

        entry_id += 1
        rhg_entry = {
            "id": f"rlf_{entry_id:05d}",
            "rohingya": rohingya,
            "english_definition": english_def,
            "source": ["rlf"],
        }
        key = rohingya.lower()
        if key not in rhg_to_en:
            rhg_to_en[key] = rhg_entry
        else:
            existing = rhg_to_en[key]
            if english_def not in existing["english_definition"]:
                existing["english_definition"] += "; " + english_def

    for key, rlf_entry in rhg_to_en.items():
        english_def = rlf_entry["english_definition"]
        en_key = english_def.lower().split(";")[0].strip()

        if en_key in en_to_rhg:
            wp_entry = en_to_rhg[en_key]
            rhg_word = rlf_entry["rohingya"]
            if rhg_word not in wp_entry["rohingya"]:
                wp_entry["rohingya"].append(rhg_word)
            if not wp_entry["definition_en"]:
                wp_entry["definition_en"] = english_def
            if "rlf" not in wp_entry["source"]:
                wp_entry["source"].append("rlf")

    unified = []

    for entry in en_to_rhg.values():
        unified.append({
            "id": entry["id"],
            "english": entry["english"],
            "rohingya": entry["rohingya"],
            "pos": entry["pos"],
            "definition": entry.get("definition_en", ""),
            "source": entry["source"],
        })

    wp_rohingya_words = set()
    for entry in en_to_rhg.values():
        for r in entry["rohingya"]:
            wp_rohingya_words.add(r.lower())

    for key, rlf_entry in rhg_to_en.items():
        if key not in wp_rohingya_words:
            unified.append({
                "id": rlf_entry["id"],
                "english": rlf_entry["english_definition"],
                "rohingya": [rlf_entry["rohingya"]],
                "pos": [],
                "definition": rlf_entry["english_definition"],
                "source": rlf_entry["source"],
            })

    unified.sort(key=lambda e: e["english"].lower())
    return unified


def generate_rag_corpus(dictionary: list[dict]) -> list[dict]:
    corpus = []
    for entry in dictionary:
        rhg_str = ", ".join(entry["rohingya"])
        pos_str = f" ({', '.join(entry['pos'])})" if entry["pos"] else ""
        defn = entry.get("definition", "")
        defn_str = f" Definition: {defn}" if defn else ""

        text_en_to_rhg = (
            f"English: {entry['english']}{pos_str} -> "
            f"Rohingya: {rhg_str}.{defn_str}"
        )
        corpus.append({
            "id": entry["id"] + "_en2rhg",
            "text": text_en_to_rhg,
            "metadata": {
                "english": entry["english"],
                "rohingya": entry["rohingya"],
                "pos": entry["pos"],
                "direction": "en-rhg",
                "source": entry["source"],
            },
        })

        for rhg_word in entry["rohingya"]:
            text_rhg_to_en = (
                f"Rohingya: {rhg_word} -> "
                f"English: {entry['english']}{pos_str}.{defn_str}"
            )
            corpus.append({
                "id": entry["id"] + f"_rhg2en_{rhg_word[:20]}",
                "text": text_rhg_to_en,
                "metadata": {
                    "english": entry["english"],
                    "rohingya": [rhg_word],
                    "pos": entry["pos"],
                    "direction": "rhg-en",
                    "source": entry["source"],
                },
            })

    return corpus


def generate_finetune_pairs(dictionary: list[dict]) -> list[dict]:
    pairs = []
    for entry in dictionary:
        rhg_str = ", ".join(entry["rohingya"])
        pos_str = f" ({', '.join(entry['pos'])})" if entry["pos"] else ""
        defn = entry.get("definition", "")

        pairs.append({
            "instruction": "Translate the following English word or phrase to Rohingya.",
            "input": entry["english"],
            "output": f"{rhg_str}{pos_str}",
        })

        for rhg_word in entry["rohingya"]:
            output = entry["english"]
            if pos_str:
                output += pos_str
            if defn and defn.lower() != entry["english"].lower():
                output += f" - {defn}"

            pairs.append({
                "instruction": "Translate the following Rohingya word or phrase to English.",
                "input": rhg_word,
                "output": output,
            })

    return pairs


def main():
    print("Loading raw data ...")
    wp_data = load_wordpress()
    rlf_data = load_rlf()
    print(f"  WordPress: {len(wp_data):,} entries")
    print(f"  RLF:       {len(rlf_data):,} entries")

    print("\nBuilding unified dictionary ...")
    dictionary = build_unified_dictionary(wp_data, rlf_data)
    print(f"  Unified: {len(dictionary):,} entries")

    with open(OUT_DICT, "w", encoding="utf-8") as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)
    print(f"  Written {OUT_DICT}")

    print("\nGenerating RAG corpus ...")
    rag = generate_rag_corpus(dictionary)
    print(f"  Documents: {len(rag):,}")
    with open(OUT_RAG, "w", encoding="utf-8") as f:
        json.dump(rag, f, ensure_ascii=False, indent=2)
    print(f"  Written {OUT_RAG}")

    print("\nGenerating fine-tuning pairs ...")
    pairs = generate_finetune_pairs(dictionary)
    print(f"  Pairs: {len(pairs):,}")
    with open(OUT_FT, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"  Written {OUT_FT}")

    print("\n--- Summary ---")
    print(f"  dictionary.json:      {len(dictionary):,} entries")
    print(f"  rag_corpus.json:      {len(rag):,} documents")
    print(f"  finetune_pairs.jsonl: {len(pairs):,} pairs")

    src_counts = {"wordpress": 0, "rlf": 0, "both": 0}
    for e in dictionary:
        if "wordpress" in e["source"] and "rlf" in e["source"]:
            src_counts["both"] += 1
        elif "wordpress" in e["source"]:
            src_counts["wordpress"] += 1
        else:
            src_counts["rlf"] += 1
    print(f"  Source distribution: {src_counts}")

    print("\nSample dictionary entries:")
    for e in dictionary[:3]:
        print(f"  {e['english']}: {e['rohingya'][:3]} {e['pos']}")
    print("\nSample fine-tuning pairs:")
    for p in pairs[:2]:
        print(f"  [{p['instruction'][:50]}] {p['input']} -> {p['output'][:60]}")


if __name__ == "__main__":
    main()
