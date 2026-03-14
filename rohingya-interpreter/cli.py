#!/usr/bin/env python3
"""CLI for Rohingya–English translation interpreter."""

import argparse
import sys

from src.interpreter import translate, RohingyaInterpreter


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Translate between English and Rohingya using RAG + local LLM (Ollama)."
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to translate (or read from stdin if omitted)",
    )
    parser.add_argument(
        "-d",
        "--direction",
        choices=["en2rhg", "rhg2en"],
        default="en2rhg",
        help="Translation direction: en2rhg (English→Rohingya) or rhg2en (Rohingya→English)",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="llama3.2:3b",
        help="Ollama model name (default: llama3.2:3b)",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:11434/v1",
        help="Ollama API base URL",
    )
    parser.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=10,
        help="Number of dictionary entries to retrieve (default: 10)",
    )
    args = parser.parse_args()

    if args.text:
        text = args.text
    else:
        text = sys.stdin.read().strip()

    if not text:
        print("Error: No text to translate. Provide text as argument or via stdin.", file=sys.stderr)
        return 1

    try:
        result = translate(
            text,
            direction=args.direction,
            model=args.model,
            base_url=args.base_url,
            top_k=args.top_k,
        )
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
