"""Narrative / psychology generator: goals, fears, quirks, and a short bio.

The ``bio`` is a deterministic template assembled from already-generated
attributes (no LLM). For richer freeform prose, use the optional
:mod:`persona_factory.enrichment` module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.data import load_json
from persona_factory.generators._helpers import pick_sample
from persona_factory.generators.base import Generator, register
from persona_factory.models.persona import Narrative

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG


class NarrativeGenerator(Generator):
    domain = "narrative"
    # run last so the bio can reference other domains
    depends_on = ("identity", "socioeconomic", "personality", "location", "lifestyle")

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        lex = load_json("lexicons", "narrative.json")
        narrative = Narrative(
            goals=pick_sample(rng, config, "narrative.goals", lex["goals"], k=2),
            fears=pick_sample(rng, config, "narrative.fears", lex["fears"], k=2),
            motivations=pick_sample(
                rng, config, "narrative.motivations", lex["motivations"], k=2
            ),
            pet_peeves=pick_sample(
                rng, config, "narrative.pet_peeves", lex["pet_peeves"], k=rng.randint(1, 2)
            ),
            quirks=pick_sample(
                rng, config, "narrative.quirks", lex["quirks"], k=rng.randint(1, 2)
            ),
        )
        if rng.chance(0.5):
            narrative.life_events = pick_sample(
                rng, config, "narrative.life_events", lex["life_events"], k=1
            )
        if rng.chance(0.3):
            narrative.secrets = pick_sample(
                rng, config, "narrative.secrets", lex["secrets"], k=1
            )
        narrative.bio = _template_bio(persona)
        persona.narrative = narrative


def _template_bio(persona: Persona) -> str:
    """Assemble a one-paragraph bio from structured attributes (no LLM)."""
    ident = persona.identity
    name = ident.given_name or persona.display_name
    parts: list[str] = []

    if ident.age and ident.nationality:
        parts.append(f"{name} is a {ident.age}-year-old from {ident.nationality}")
    elif ident.age:
        parts.append(f"{name} is {ident.age} years old")
    else:
        parts.append(name)

    socio = persona.socioeconomic
    if socio and socio.occupation:
        sentence = f"who works as a {socio.occupation}"
        if socio.industry:
            sentence += f" in {socio.industry.lower()}"
        parts.append(sentence)

    base = " ".join(parts).rstrip(".") + "."

    extra: list[str] = []
    pers = persona.personality
    if pers and pers.traits:
        extra.append(f"They come across as {', '.join(pers.traits[:3])}.")
    life = persona.lifestyle
    if life and life.hobbies:
        extra.append(f"In their free time they enjoy {', '.join(life.hobbies[:3])}.")
    if persona.narrative and persona.narrative.goals:
        extra.append(f"They hope to {persona.narrative.goals[0]}.")

    return " ".join([base, *extra]).strip()


register(NarrativeGenerator())
