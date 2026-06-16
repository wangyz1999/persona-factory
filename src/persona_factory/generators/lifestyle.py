"""Lifestyle / behavioral generator: hobbies, diet, health, habits, tech."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.data import load_json
from persona_factory.generators._helpers import as_enum, pick, pick_sample
from persona_factory.generators.base import Generator, register
from persona_factory.models.enums import (
    Chronotype,
    Diet,
    FitnessLevel,
    SubstanceUse,
    TechSavviness,
)
from persona_factory.models.persona import Lifestyle

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG

_DIET_WEIGHTS = {
    Diet.OMNIVORE: 0.6,
    Diet.FLEXITARIAN: 0.13,
    Diet.VEGETARIAN: 0.1,
    Diet.PESCATARIAN: 0.06,
    Diet.VEGAN: 0.04,
    Diet.HALAL: 0.03,
    Diet.KOSHER: 0.02,
    Diet.KETO: 0.02,
}
_SUBSTANCE_WEIGHTS = [0.4, 0.25, 0.2, 0.1, 0.05]


class LifestyleGenerator(Generator):
    domain = "lifestyle"

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        lex = load_json("lexicons", "lifestyle.json")
        lifestyle = Lifestyle(
            hobbies=pick_sample(
                rng, config, "lifestyle.hobbies", lex["hobbies"], k=rng.randint(2, 4)
            ),
            interests=pick_sample(
                rng, config, "lifestyle.interests", lex["interests"], k=rng.randint(2, 4)
            ),
            skills=pick_sample(rng, config, "lifestyle.skills", lex["skills"], k=rng.randint(2, 3)),
            favorite_media=pick_sample(rng, config, "lifestyle.favorite_media", lex["media"], k=2),
            diet=as_enum(
                pick(
                    rng,
                    config,
                    "lifestyle.diet",
                    list(_DIET_WEIGHTS),
                    list(_DIET_WEIGHTS.values()),
                ),
                Diet,
            ),
            fitness_level=as_enum(
                pick(rng, config, "lifestyle.fitness_level", list(FitnessLevel)),
                FitnessLevel,
            ),
            smoking=as_enum(
                pick(rng, config, "lifestyle.smoking", list(SubstanceUse), _SUBSTANCE_WEIGHTS),
                SubstanceUse,
            ),
            alcohol=as_enum(
                pick(rng, config, "lifestyle.alcohol", list(SubstanceUse), _SUBSTANCE_WEIGHTS),
                SubstanceUse,
            ),
            chronotype=as_enum(
                pick(rng, config, "lifestyle.chronotype", list(Chronotype)),
                Chronotype,
            ),
            tech_savviness=as_enum(
                pick(rng, config, "lifestyle.tech_savviness", list(TechSavviness)),
                TechSavviness,
            ),
        )
        # ~25% have an allergy
        if rng.chance(0.25):
            lifestyle.allergies = pick_sample(
                rng, config, "lifestyle.allergies", lex["allergies"], k=rng.randint(1, 2)
            )
        persona.lifestyle = lifestyle


register(LifestyleGenerator())
