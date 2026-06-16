"""Optionally enrich a persona's backstory with Claude.

Requires the enrichment extra and an API key:
    uv sync --extra enrichment
    export ANTHROPIC_API_KEY=sk-ant-...
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
