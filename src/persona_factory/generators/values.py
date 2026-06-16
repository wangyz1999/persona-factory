"""Values & character generator: core values, moral foundations, strengths."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.data import load_json
from persona_factory.generators._helpers import pick_sample
from persona_factory.generators.base import Generator, register
from persona_factory.models.persona import Values

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG


class ValuesGenerator(Generator):
    domain = "values"

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        lex = load_json("lexicons", "values.json")
        persona.values = Values(
            core_values=pick_sample(
                rng, config, "values.core_values", lex["core_values"], k=3
            ),
            moral_foundations=pick_sample(
                rng, config, "values.moral_foundations", lex["moral_foundations"], k=2
            ),
            character_strengths=pick_sample(
                rng,
                config,
                "values.character_strengths",
                lex["character_strengths"],
                k=3,
            ),
        )


register(ValuesGenerator())
