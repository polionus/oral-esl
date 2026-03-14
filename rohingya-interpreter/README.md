# Rohingya Translation Interpreter

RAG-based English–Rohingya translator using a local LLM (Ollama). Uses the [rohingya-dict](../rohingya-dict) dictionary and grammar as the knowledge base.

## Prerequisites

1. **Ollama** – Install from [ollama.com](https://ollama.com) and run locally.
2. **A model** – Pull a multilingual model, e.g.:
   ```bash
   ollama pull llama3.2:3b
   # or
   ollama pull mistral:7b
   ```

## Setup

```bash
cd rohingya-interpreter
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Ensure the [rohingya-dict](../rohingya-dict) pipeline has been run so that `output/rag_corpus.json` and `output/dictionary.json` exist.

## Usage

### CLI

```bash
# English → Rohingya (default)
python cli.py "hello"
python cli.py -d en2rhg "good morning"

# Rohingya → English
python cli.py -d rhg2en "Assólamu aláikum"

# From stdin
echo "thank you" | python cli.py -d en2rhg

# Custom model
python cli.py -m mistral:7b "water"
```

### Python API

```python
from src.interpreter import translate, RohingyaInterpreter

# One-off translation
result = translate("hello", direction="en2rhg")
print(result)  # e.g. "salam" or similar from dictionary

# Reusable interpreter (caches RAG index)
interp = RohingyaInterpreter(model="llama3.2:3b")
rohingya = interp.to_rohingya("I am eating food")
english = interp.to_english("Ãi hana hair.")
```

## How It Works

1. **RAG**: Your input is embedded and used to retrieve relevant entries from the dictionary (rag_corpus.json). For **sentences**, the system runs retrieval on both the full sentence and each content word, then merges results—ensuring dictionary coverage for all words.
2. **Grammar**: Rohingya grammar rules (SOV, pronouns, noun classes, verb conjugation) are loaded from grammar_notes.json and added to the system prompt.
3. **LLM**: The local model (via Ollama) receives the retrieved entries and grammar, then produces the translation. Output is cleaned to return only the translated text.

The first run builds a ChromaDB index (stored in `.chroma/`), which can take a few minutes for ~275k documents. Later runs reuse the index.

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--direction` | en2rhg | `en2rhg` or `rhg2en` |
| `--model` | llama3.2:3b | Ollama model name |
| `--base-url` | http://localhost:11434/v1 | Ollama API URL |
| `--top-k` | 10 | Number of dictionary entries to retrieve |

## Troubleshooting

- **"Connection refused"** – Start Ollama: `ollama serve` (or launch the Ollama app).
- **"Model not found"** – Run `ollama pull llama3.2:3b`.
- **Slow first run** – The RAG index is built on first use (~5–10 min for full corpus).
