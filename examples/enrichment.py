"""Optionally enrich a persona's backstory with an LLM.

Core generation is offline; this step calls a model. It defaults to Anthropic,
but ``enrich(..., provider="openai")`` and ``provider="openrouter"`` also work.

    export ANTHROPIC_API_KEY=sk-ant-...   # or OPENAI_API_KEY / OPENROUTER_API_KEY
    uv run python examples/enrichment.py
"""

from __future__ import annotations

import os

from persona_factory import PersonaFactory
from persona_factory.enrichment import enrich


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY to run this example.")
        return

    person = PersonaFactory("en_US", seed=42).generate()
    print("Templated bio (offline):")
    print(" ", person.narrative.bio)

    enrich(person, backstory=True, sample_dialogue=True)

    print("\nEnriched backstory (Claude):")
    print(" ", person.narrative.backstory)
    print("\nSample dialogue:")
    for line in person.narrative.sample_dialogue:
        print("  -", line)


if __name__ == "__main__":
    main()
