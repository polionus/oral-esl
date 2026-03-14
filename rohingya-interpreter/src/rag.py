"""RAG pipeline: embeddings, vector store, retrieval for Rohingya dictionary."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


Direction = Literal["en2rhg", "rhg2en"]

# Words to skip in per-word retrieval (articles rarely have standalone dictionary entries)
EN_SKIP_WORDS = frozenset({"a", "an", "the"})

# Paths relative to rohingya-interpreter root
ROOT = Path(__file__).resolve().parent.parent
DICT_ROOT = ROOT.parent / "rohingya-dict"
RAG_CORPUS = DICT_ROOT / "output" / "rag_corpus.json"
DICTIONARY = DICT_ROOT / "output" / "dictionary.json"
CHROMA_PERSIST = ROOT / ".chroma"
COLLECTION_NAME = "rohingya_dict"


def _direction_to_metadata(direction: Direction) -> str:
    """Map direction to rag_corpus metadata direction value."""
    return "en-rhg" if direction == "en2rhg" else "rhg-en"


def load_rag_corpus(path: Path | None = None) -> list[dict]:
    """Load RAG corpus from JSON."""
    path = path or RAG_CORPUS
    if not path.exists():
        raise FileNotFoundError(f"RAG corpus not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_dictionary(path: Path | None = None) -> list[dict]:
    """Load dictionary for fallback lookup."""
    path = path or DICTIONARY
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class RAGRetriever:
    """Retrieve relevant dictionary entries via semantic search."""

    def __init__(
        self,
        corpus_path: Path | None = None,
        persist_dir: Path | None = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        top_k: int = 10,
    ):
        self.corpus_path = corpus_path or RAG_CORPUS
        self.persist_dir = persist_dir or CHROMA_PERSIST
        self.embedding_model_name = embedding_model
        self.top_k = top_k
        self._embedder: SentenceTransformer | None = None
        self._client: chromadb.PersistentClient | None = None
        self._collection = None

    @property
    def embedder(self) -> SentenceTransformer:
        if self._embedder is None:
            self._embedder = SentenceTransformer(self.embedding_model_name)
        return self._embedder

    @staticmethod
    def _deduplicate_ids(ids: list[str]) -> list[str]:
        """Ensure unique IDs by appending _1, _2, ... for duplicates."""
        seen: dict[str, int] = {}
        result = []
        for id_ in ids:
            if id_ not in seen:
                seen[id_] = 0
                result.append(id_)
            else:
                seen[id_] += 1
                result.append(f"{id_}_{seen[id_]}")
        return result

    def _get_collection(self, direction: Direction):
        """Get or create Chroma collection for the given direction."""
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False),
            )
        coll_name = f"{COLLECTION_NAME}_{direction}"
        return self._client.get_or_create_collection(
            name=coll_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _build_index(self, direction: Direction) -> None:
        """Build Chroma index from RAG corpus for the given direction."""
        corpus = load_rag_corpus(self.corpus_path)
        target_dir = _direction_to_metadata(direction)
        docs = [d for d in corpus if d.get("metadata", {}).get("direction") == target_dir]
        if not docs:
            return
        texts = [d["text"] for d in docs]
        raw_ids = [d["id"] for d in docs]
        # ChromaDB requires unique IDs; corpus may have duplicates (e.g. rhg2en truncation)
        ids = self._deduplicate_ids(raw_ids)
        embeddings = self.embedder.encode(texts, show_progress_bar=True, batch_size=128)
        coll = self._get_collection(direction)
        # ChromaDB has a max batch size (~5461); add in chunks to avoid ValueError
        max_batch = 5000
        for i in range(0, len(ids), max_batch):
            end = min(i + max_batch, len(ids))
            coll.add(
                ids=ids[i:end],
                embeddings=embeddings[i:end].tolist(),
                documents=texts[i:end],
            )

    def ensure_index(self, direction: Direction) -> None:
        """Ensure index exists; build if missing."""
        coll = self._get_collection(direction)
        if coll.count() == 0:
            self._build_index(direction)

    @staticmethod
    def _tokenize_for_retrieval(text: str, direction: Direction) -> list[str]:
        """Extract meaningful tokens for per-word retrieval."""
        # Simple tokenization: split on non-alphanumeric, keep words 2+ chars
        words = re.findall(r"[a-zA-Zãẽĩõũñçáéíóúàèìòùâêîôû]+", text, re.IGNORECASE)
        if direction == "en2rhg":
            return [w for w in words if len(w) >= 2 and w.lower() not in EN_SKIP_WORDS]
        return [w for w in words if len(w) >= 2]

    def retrieve(
        self,
        query: str,
        direction: Direction,
        top_k: int | None = None,
    ) -> list[str]:
        """Retrieve top-k relevant dictionary entries as text snippets.

        For sentences (multiple words), runs retrieval on the full sentence AND on
        individual content words, then merges and deduplicates. This ensures we get
        dictionary entries for all words in the sentence, not just the top-K for the
        whole phrase.
        """
        k = top_k or self.top_k
        self.ensure_index(direction)
        coll = self._get_collection(direction)
        n = coll.count()
        if n == 0:
            return []

        tokens = self._tokenize_for_retrieval(query, direction)
        is_sentence = len(tokens) >= 2

        if is_sentence:
            # Multi-query retrieval: whole sentence + each significant word
            k_per_query = max(3, k // (len(tokens) + 1))
            all_queries = [query] + tokens
            all_embeddings = self.embedder.encode(all_queries, show_progress_bar=False)
            seen: set[str] = set()
            merged: list[str] = []
            for i, q in enumerate(all_queries):
                emb = [all_embeddings[i].tolist()]
                results = coll.query(
                    query_embeddings=emb,
                    n_results=min(k_per_query, n),
                )
                if results and results.get("documents") and results["documents"][0]:
                    for doc in results["documents"][0]:
                        if doc not in seen:
                            seen.add(doc)
                            merged.append(doc)
            return merged[:k * 2]  # Allow more context for sentences
        else:
            # Single word/phrase: standard retrieval
            query_embedding = self.embedder.encode([query]).tolist()
            results = coll.query(
                query_embeddings=query_embedding,
                n_results=min(k, n),
            )
            if results and results.get("documents") and results["documents"][0]:
                return results["documents"][0]
        return []


def _extract_tokens(text: str) -> list[str]:
    """Extract alphanumeric tokens from text."""
    return [w for w in re.findall(r"[a-zA-Zãẽĩõũñçáéíóúàèìòùâêîôû]+", text) if len(w) >= 2]


def dict_fallback_lookup(
    text: str,
    direction: Direction,
    dictionary: list[dict] | None = None,
) -> list[str]:
    """Exact or substring lookup in dictionary when retrieval misses.

    For multi-word input, also looks up each word individually to gather
    translations for sentence building.
    """
    dictionary = dictionary or load_dictionary()
    text_lower = text.lower().strip()
    seen: set[str] = set()
    matches: list[str] = []

    def add_match(s: str) -> None:
        if s not in seen:
            seen.add(s)
            matches.append(s)

    # Whole-phrase match first
    for entry in dictionary:
        en = (entry.get("english") or "").lower()
        rhg_list = entry.get("rohingya") or []
        if direction == "en2rhg":
            if text_lower in en or en in text_lower:
                for r in rhg_list:
                    add_match(f"English: {entry['english']} -> Rohingya: {r}")
        else:
            for r in rhg_list:
                if text_lower in r.lower() or r.lower() in text_lower:
                    add_match(f"Rohingya: {r} -> English: {entry['english']}")

    # For sentences: also look up each word individually (handles "eating" -> "eat")
    tokens = _extract_tokens(text_lower)
    if len(tokens) >= 2:
        for word in tokens:
            if word in {"a", "an", "the"}:
                continue
            for entry in dictionary:
                en = (entry.get("english") or "").lower()
                rhg_list = entry.get("rohingya") or []
                if direction == "en2rhg":
                    # Match: exact, or word/entry share stem (e.g. eating <-> eat)
                    en_word = en.split()[0] if en else ""
                    if word == en or en == word or word in en or en in word or word == en_word:
                        for r in rhg_list:
                            add_match(f"English: {entry['english']} -> Rohingya: {r}")
                else:
                    for r in rhg_list:
                        if word in r.lower() or r.lower() in word:
                            add_match(f"Rohingya: {r} -> English: {entry['english']}")

    return matches[:15]  # Allow more for sentence context
