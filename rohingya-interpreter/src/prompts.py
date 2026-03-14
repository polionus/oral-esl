"""Prompt building for Rohingya translation with grammar and dictionary context."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

Direction = Literal["en2rhg", "rhg2en"]

ROOT = Path(__file__).resolve().parent.parent
DICT_ROOT = ROOT.parent / "rohingya-dict"
GRAMMAR_PATH = DICT_ROOT / "grammar" / "grammar_notes.json"


def load_grammar_summary(path: Path | None = None) -> str:
    """Load grammar notes and produce a concise summary for the system prompt."""
    path = path or GRAMMAR_PATH
    if not path.exists():
        return "Rohingya is an Indo-Aryan language. Use the provided dictionary for translations."
    with open(path, encoding="utf-8") as f:
        g = json.load(f)
    parts = []
    parts.append(f"Language: {g.get('language', 'Rohingya')} ({g.get('iso_code', 'rhg')})")
    parts.append(f"Word order: {g.get('word_order', 'SOV')}")
    if "word_order_examples" in g:
        ex = g["word_order_examples"][:2]
        parts.append("Examples: " + "; ".join(f"{e['rohingya']} = {e['gloss']}" for e in ex))
    if "noun_classes" in g:
        nc = g["noun_classes"]
        parts.append(f"Noun classes: {nc.get('description', '')[:80]}...")
    if "common_phrases" in g:
        phrases = g["common_phrases"][:3]
        parts.append("Common: " + ", ".join(f"{p['rohingya']} ({p['english']})" for p in phrases))
    return "\n".join(parts)


def build_system_prompt(grammar_summary: str) -> str:
    """Build the system prompt with grammar context."""
    return f"""You are a Rohingya–English translator. Use ONLY the dictionary entries provided in the context to translate. Do not invent translations.

Rohingya grammar summary:
{grammar_summary}

When translating:
- For single words/phrases: return the exact translation from the dictionary.
- For sentences: combine dictionary entries following Rohingya SOV word order.
- Preserve Rohingyalish spelling (ã, ñ, ç, etc.).
- If the input is not in the dictionary, say "Translation not found" and suggest the closest match if any."""


def build_user_prompt(
    text: str,
    direction: Direction,
    context_entries: list[str],
) -> str:
    """Build the user prompt with retrieved dictionary context."""
    dir_desc = "English to Rohingya" if direction == "en2rhg" else "Rohingya to English"
    context_block = "\n".join(context_entries) if context_entries else "(No dictionary entries retrieved)"
    return f"""Relevant dictionary entries ({dir_desc}):
{context_block}

---
Translate the following from {dir_desc}:

"{text}"

Translation:"""
