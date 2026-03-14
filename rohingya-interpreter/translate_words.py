#!/usr/bin/env python3
"""Translate a list of English words/phrases to Rohingya and save as word pairs."""

from src.interpreter import RohingyaInterpreter

WORDS = [
    "go",
    "come",
    "make",
    "take",
    "get",
    "give",
    "find",
    "tell",
    "work",
    "call",
    "try",
    "ask",
    "need",
    "feel",
    "leave",
    "put",
    "keep",
    "let",
    "bad",
    "big",
    "small",
    "new",
    "old",
    "high",
    "low",
    "different",
    "same",
    "important",
    "Good evening",
    "How are you?",
    "Nice to meet you",
    "Can you help me?",
    "I need help",
    "Please help me",
    "Could you repeat that?",
    "I am hungry",
    "I am thirsty",
    "I am sick",
    "I need water",
]


def main():
    interp = RohingyaInterpreter()
    pairs = []
    for i, word in enumerate(WORDS):
        print(f"[{i + 1}/{len(WORDS)}] Translating: {word}")
        try:
            rohingya = interp.to_rohingya(word)
            pairs.append((word, rohingya))
        except Exception as e:
            pairs.append((word, f"[Error: {e}]"))
            print(f"  Error: {e}")

    with open("translations.txt", "w", encoding="utf-8") as f:
        for eng, rhg in pairs:
            f.write(f"{eng}\t{rhg}\n")

    print(f"\nWrote {len(pairs)} word pairs to translations.txt")


if __name__ == "__main__":
    main()
