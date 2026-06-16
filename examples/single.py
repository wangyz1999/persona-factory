"""Generate a single persona and render it three ways.

Run with:  uv run python examples/single.py
"""

from __future__ import annotations

from persona_factory import PersonaFactory


def main() -> None:
    factory = PersonaFactory(locale="en_US", seed=42)
    person = factory.generate(gender="female", age_range=(25, 35), mbti="INTJ")

    print("=" * 70)
    print("MARKDOWN CARD")
    print("=" * 70)
    print(person.to_markdown_card())

    print("=" * 70)
    print("LLM SYSTEM PROMPT (roleplay)")
    print("=" * 70)
    print(person.to_system_prompt())

    print()
    print("=" * 70)
    print("JSON (first 400 chars)")
    print("=" * 70)
    print(person.to_json()[:400], "...")


if __name__ == "__main__":
    main()
