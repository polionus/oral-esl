"""RAG pipeline: embeddings, vector store, retrieval for Rohingya dictionary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


Direction = Literal["en2rhg", "rhg2en"]

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
        ids = [d["id"] for d in docs]
        embeddings = self.embedder.encode(texts, show_progress_bar=True, batch_size=128)
        coll = self._get_collection(direction)
        coll.add(ids=ids, embeddings=embeddings.tolist(), documents=texts)

    def ensure_index(self, direction: Direction) -> None:
        """Ensure index exists; build if missing."""
        coll = self._get_collection(direction)
        if coll.count() == 0:
            self._build_index(direction)

    def retrieve(
        self,
        query: str,
        direction: Direction,
        top_k: int | None = None,
    ) -> list[str]:
        """Retrieve top-k relevant dictionary entries as text snippets."""
        k = top_k or self.top_k
        self.ensure_index(direction)
        coll = self._get_collection(direction)
        n = coll.count()
        if n == 0:
            return []
        query_embedding = self.embedder.encode([query]).tolist()
        results = coll.query(
            query_embeddings=query_embedding,
            n_results=min(k, n),
        )
        if results and results.get("documents") and results["documents"][0]:
            return results["documents"][0]
        return []


def dict_fallback_lookup(
    text: str,
    direction: Direction,
    dictionary: list[dict] | None = None,
) -> list[str]:
    """Exact or substring lookup in dictionary when retrieval misses."""
    dictionary = dictionary or load_dictionary()
    text_lower = text.lower().strip()
    matches = []
    for entry in dictionary:
        en = (entry.get("english") or "").lower()
        rhg_list = entry.get("rohingya") or []
        if direction == "en2rhg":
            if text_lower in en or en in text_lower:
                for r in rhg_list:
                    matches.append(f"English: {entry['english']} -> Rohingya: {r}")
        else:
            for r in rhg_list:
                if text_lower in r.lower() or r.lower() in text_lower:
                    matches.append(f"Rohingya: {r} -> English: {entry['english']}")
    return matches[:5]  # Limit fallback results
