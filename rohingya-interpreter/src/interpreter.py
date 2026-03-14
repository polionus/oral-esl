"""Rohingya–English translation interpreter: RAG + local LLM."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from openai import OpenAI

from .prompts import build_system_prompt, build_user_prompt, load_grammar_summary
from .rag import RAGRetriever, dict_fallback_lookup, load_dictionary

Direction = Literal["en2rhg", "rhg2en"]

# Default Ollama endpoint
OLLAMA_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3.2:3b"


def translate(
    text: str,
    direction: Direction = "en2rhg",
    *,
    model: str = DEFAULT_MODEL,
    base_url: str = OLLAMA_BASE_URL,
    api_key: str = "ollama",
    top_k: int = 10,
    retriever: RAGRetriever | None = None,
) -> str:
    """
    Translate text between English and Rohingya using RAG + local LLM.

    Args:
        text: Input text to translate.
        direction: "en2rhg" for English→Rohingya, "rhg2en" for Rohingya→English.
        model: Ollama model name (e.g. llama3.2:3b, mistral:7b).
        base_url: Ollama API base URL.
        api_key: API key (Ollama ignores this; use any string).
        top_k: Number of dictionary entries to retrieve for context.
        retriever: Optional pre-built RAGRetriever (reused for multiple calls).

    Returns:
        Translated text.
    """
    if not text or not text.strip():
        return ""

    retriever = retriever or RAGRetriever(top_k=top_k)
    entries = retriever.retrieve(text.strip(), direction, top_k=top_k)
    if not entries:
        entries = dict_fallback_lookup(text.strip(), direction)
    grammar = load_grammar_summary()
    system_prompt = build_system_prompt(grammar)
    user_prompt = build_user_prompt(text.strip(), direction, entries)

    client = OpenAI(base_url=base_url, api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )
    result = response.choices[0].message.content
    return (result or "").strip()


class RohingyaInterpreter:
    """
    Stateful interpreter that reuses RAG retriever and optional config.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        top_k: int = 10,
    ):
        self.model = model
        self.base_url = base_url
        self.top_k = top_k
        self._retriever = RAGRetriever(top_k=top_k)

    def translate(self, text: str, direction: Direction = "en2rhg") -> str:
        """Translate text."""
        return translate(
            text,
            direction,
            model=self.model,
            base_url=self.base_url,
            top_k=self.top_k,
            retriever=self._retriever,
        )

    def to_rohingya(self, text: str) -> str:
        """Translate English to Rohingya."""
        return self.translate(text, "en2rhg")

    def to_english(self, text: str) -> str:
        """Translate Rohingya to English."""
        return self.translate(text, "rhg2en")
