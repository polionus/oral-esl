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
    parts.append(f"Word order: {g.get('word_order', 'SOV')} — Subject comes first, then Object, then Verb.")
    if "word_order_examples" in g:
        ex = g["word_order_examples"][:4]
        parts.append("SOV examples: " + "; ".join(f"{e['rohingya']} = {e['gloss']}" for e in ex))
    if "pronouns" in g and "personal" in g["pronouns"]:
        p = g["pronouns"]["personal"]
        parts.append("Pronouns (ergative): I=ãi, you=tui/tũi, he=hite, she=hiba, we=ãra, they=hitara")
    if "verb_conjugation" in g and "tenses" in g["verb_conjugation"]:
        vc = g["verb_conjugation"]["tenses"]
        if "present_progressive" in vc:
            pp = vc["present_progressive"]
            parts.append(f"Present progressive: {pp.get('forms', {})}")
    if "noun_classes" in g:
        nc = g["noun_classes"]
        parts.append(f"Noun classes: {nc.get('description', '')[:80]}...")
    if "common_phrases" in g:
        phrases = g["common_phrases"][:4]
        parts.append("Common: " + ", ".join(f"{p['rohingya']} ({p['english']})" for p in phrases))
    return "\n".join(parts)


def build_system_prompt(grammar_summary: str) -> str:
    """Build the system prompt with grammar context."""
    return f"""You are a Rohingya–English translator. Use the dictionary entries provided in the context. Prefer dictionary translations; only infer from grammar when combining words.

Rohingya grammar summary:
{grammar_summary}

Translation rules:
- Single words/phrases: return the exact translation from the dictionary.
- Sentences: (1) Identify each word's translation from the context. (2) Arrange in SOV order: Subject first, Object second, Verb last. (3) Apply verb conjugation (e.g. "I am eating food" → Ãi hana hair.). (4) Use pronouns from the grammar (I=ãi, you=tui, he=hite, she=hiba).
- Preserve Rohingyalish spelling (ã, ñ, ç, á, etc.).
- If a word has no dictionary match, try the closest related form (e.g. "eating" → use "eat" entry).
- If nothing matches, say "Translation not found" and suggest the closest match if any.

IMPORTANT: Output ONLY the translation. No explanations, no bullet points, no "The translation is...". Just the translated text."""


def build_user_prompt(
    text: str,
    direction: Direction,
    context_entries: list[str],
    phrase_entries: list[str] | None = None,
) -> str:
    """Build the user prompt with retrieved dictionary context."""
    dir_desc = "English to Rohingya" if direction == "en2rhg" else "Rohingya to English"
    parts: list[str] = []
    if phrase_entries:
        parts.append("Relevant common phrases (prefer these when input matches):")
        parts.append("\n".join(phrase_entries))
        parts.append("")
    parts.append("Dictionary entries:")
    parts.append("\n".join(context_entries) if context_entries else "(No dictionary entries retrieved)")
    context_block = "\n".join(parts)
    word_count = len([w for w in text.split() if len(w) >= 2])
    sentence_hint = (
        " (This is a sentence — combine the entries above in SOV order.)"
        if word_count >= 2 and direction == "en2rhg"
        else ""
    )
    return f"""Context for {dir_desc}:
{context_block}

---
Translate the following from {dir_desc}{sentence_hint}:

"{text}"

Output only the translation (no explanation):"""
