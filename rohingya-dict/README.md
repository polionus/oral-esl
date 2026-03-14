# Rohingya Dictionary Pipeline

Scrapes, parses, and merges online Rohingya–English dictionary resources into
clean structured datasets suitable for RAG retrieval or LLM fine-tuning.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the scripts in order:

```bash
# 1. Scrape sources
python scrape/wordpress_dict.py
python scrape/rlf_dict.py

# 2. Clean & merge into unified dictionary
python parse/clean.py

# 3. Outputs are written to output/
#    - dictionary.json       Unified dictionary
#    - rag_corpus.json       RAG-optimized documents
#    - finetune_pairs.jsonl  Instruction-tuning pairs
```

## Data Sources

| Source | Direction | Entries | URL |
|--------|-----------|---------|-----|
| WordPress (IOM) | EN → RHG | ~6,198 | rohingyadictionary.wordpress.com |
| Rohingyalanguage.com | RHG → EN | ~3,000+ | rohingyalanguage.com/rohingya-english-dictionary-v0 |

Both sources are Creative-Commons-licensed community resources.

## Output Formats

- **dictionary.json** – unified list of entries with English, Rohingya translations,
  part of speech, definitions, and provenance.
- **rag_corpus.json** – each entry as a self-contained text document with metadata,
  ready for embedding / vector-store ingestion.
- **finetune_pairs.jsonl** – instruction / input / output triples in both translation
  directions, compatible with Axolotl, Unsloth, LLaMA-Factory, etc.
- **grammar/grammar_notes.json** – key Rohingya grammar rules for LLM system-prompt
  context.
