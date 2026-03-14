#!/usr/bin/env python3
"""Evaluate translation accuracy using rohingya_sentences.xlsx test set."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import openpyxl

from src.interpreter import RohingyaInterpreter

ROOT = Path(__file__).resolve().parent
XLSX_PATH = ROOT.parent / "rohingya-dict" / "rohingya_sentences.xlsx"


def load_sentence_pairs(path: Path) -> list[tuple[str, str]]:
    """Load (English, Rohingya) pairs from Excel."""
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))[1:]
    return [(str(r[0]).strip(), str(r[1]).strip()) for r in rows if r[0] and r[1]]


def normalize(s: str) -> str:
    """Normalize for comparison: lowercase, strip punctuation, collapse whitespace."""
    s = s.lower().strip()
    s = re.sub(r"[^\w\sãẽĩõũñçáéíóúàèìòùâêîôû]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def exact_match(pred: str, ref: str) -> bool:
    return pred.strip() == ref.strip()


def normalized_match(pred: str, ref: str) -> bool:
    return normalize(pred) == normalize(ref)


def main() -> int:
    if not XLSX_PATH.exists():
        print(f"Error: {XLSX_PATH} not found", file=sys.stderr)
        return 1

    pairs = load_sentence_pairs(XLSX_PATH)
    print(f"Loaded {len(pairs)} sentence pairs from {XLSX_PATH.name}\n")

    interp = RohingyaInterpreter()

    # en2rhg: English -> Rohingya
    print("=" * 60)
    print("Direction: English → Rohingya (en2rhg)")
    print("=" * 60)
    en2rhg_exact = 0
    en2rhg_norm = 0
    en2rhg_results = []
    for i, (eng, rhg_ref) in enumerate(pairs):
        try:
            pred = interp.to_rohingya(eng)
            ex = exact_match(pred, rhg_ref)
            nm = normalized_match(pred, rhg_ref)
            if ex:
                en2rhg_exact += 1
            if nm:
                en2rhg_norm += 1
            en2rhg_results.append((eng, rhg_ref, pred, ex, nm))
            status = "✓" if nm else "✗"
            print(f"  [{i+1:3d}/{len(pairs)}] {status} {eng[:40]:<40} -> {pred[:35]}")
        except Exception as e:
            print(f"  [{i+1:3d}/{len(pairs)}] ERROR: {eng[:40]} - {e}", file=sys.stderr)
            en2rhg_results.append((eng, rhg_ref, f"[Error: {e}]", False, False))

    en2rhg_exact_pct = 100 * en2rhg_exact / len(pairs)
    en2rhg_norm_pct = 100 * en2rhg_norm / len(pairs)
    print(f"\nen2rhg Accuracy: exact={en2rhg_exact_pct:.1f}% ({en2rhg_exact}/{len(pairs)}), "
          f"normalized={en2rhg_norm_pct:.1f}% ({en2rhg_norm}/{len(pairs)})")

    # rhg2en: Rohingya -> English
    print("\n" + "=" * 60)
    print("Direction: Rohingya → English (rhg2en)")
    print("=" * 60)
    rhg2en_exact = 0
    rhg2en_norm = 0
    for i, (eng_ref, rhg) in enumerate(pairs):
        try:
            pred = interp.to_english(rhg)
            ex = exact_match(pred, eng_ref)
            nm = normalized_match(pred, eng_ref)
            if ex:
                rhg2en_exact += 1
            if nm:
                rhg2en_norm += 1
            status = "✓" if nm else "✗"
            print(f"  [{i+1:3d}/{len(pairs)}] {status} {rhg[:35]:<35} -> {pred[:40]}")
        except Exception as e:
            print(f"  [{i+1:3d}/{len(pairs)}] ERROR: {rhg[:35]} - {e}", file=sys.stderr)
            rhg2en_exact += 0
            rhg2en_norm += 0

    rhg2en_exact_pct = 100 * rhg2en_exact / len(pairs)
    rhg2en_norm_pct = 100 * rhg2en_norm / len(pairs)
    print(f"\nrhg2en Accuracy: exact={rhg2en_exact_pct:.1f}% ({rhg2en_exact}/{len(pairs)}), "
          f"normalized={rhg2en_norm_pct:.1f}% ({rhg2en_norm}/{len(pairs)})")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  en2rhg: exact {en2rhg_exact_pct:.1f}%, normalized {en2rhg_norm_pct:.1f}%")
    print(f"  rhg2en: exact {rhg2en_exact_pct:.1f}%, normalized {rhg2en_norm_pct:.1f}%")
    print(f"  Overall (avg normalized): {(en2rhg_norm_pct + rhg2en_norm_pct) / 2:.1f}%")

    # Save results to file
    out_path = ROOT / "eval_results.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"Evaluation on {XLSX_PATH.name} ({len(pairs)} pairs)\n")
        f.write(f"en2rhg: exact {en2rhg_exact_pct:.1f}%, normalized {en2rhg_norm_pct:.1f}%\n")
        f.write(f"rhg2en: exact {rhg2en_exact_pct:.1f}%, normalized {rhg2en_norm_pct:.1f}%\n")
    print(f"\nResults saved to {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
