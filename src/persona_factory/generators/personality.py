"""Personality generator covering multiple frameworks.

OCEAN scores are the substrate; MBTI letters are *derived* from the OCEAN draw
(so the two frameworks agree) unless the caller pins an explicit MBTI type.
Enneagram, DISC, temperament and descriptive traits are sampled on top.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.data import load_json
from persona_factory.generators._helpers import as_enum, is_fixed, pick
from persona_factory.generators.base import Generator, register
from persona_factory.models.enums import (
    DISCType,
    EnneagramType,
    MBTIType,
    Temperament,
)
from persona_factory.models.persona import BigFive, Personality

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG


class PersonalityGenerator(Generator):
    domain = "personality"

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        traits_data = load_json("personality", "traits.json")
        enneagram_data = load_json("personality", "enneagram.json")

        # -- OCEAN -------------------------------------------------------
        big_five = BigFive(
            openness=_score(rng),
            conscientiousness=_score(rng),
            extraversion=_score(rng),
            agreeableness=_score(rng),
            neuroticism=_score(rng),
        )

        personality = Personality(big_five=big_five)

        # -- MBTI (pinned or derived from OCEAN) ------------------------
        mbti_fixed = is_fixed(config, "personality.mbti")
        if mbti_fixed is not None:
            personality.mbti = MBTIType(mbti_fixed)
        else:
            personality.mbti = _mbti_from_ocean(big_five)

        # -- Enneagram (+ wing) -----------------------------------------
        enn = pick(rng, config, "personality.enneagram_type", list(EnneagramType))
        enn = enn if isinstance(enn, EnneagramType) else EnneagramType(enn)
        personality.enneagram_type = enn
        wings = enneagram_data["types"][enn.value]["wings"]
        personality.enneagram_wing = f"{enn.value}w{rng.choice(wings)}"

        # -- DISC + temperament -----------------------------------------
        personality.disc = as_enum(pick(rng, config, "personality.disc", list(DISCType)), DISCType)
        personality.temperament = as_enum(
            pick(rng, config, "personality.temperament", list(Temperament)),
            Temperament,
        )
        personality.hexaco_honesty_humility = round(_score(rng), 2)

        # -- descriptive traits derived from OCEAN extremes -------------
        personality.traits = _derive_traits(rng, big_five, traits_data)
        personality.strengths = rng.weighted_sample(traits_data["positive"], k=3)
        personality.weaknesses = rng.weighted_sample(traits_data["negative"], k=2)

        persona.personality = personality


def _score(rng: RNG) -> float:
    """A trait score in [0, 1], centered with mild spread."""
    return round(rng.bounded_gauss(0.5, 0.2, 0.0, 1.0), 2)


def _mbti_from_ocean(b: BigFive) -> MBTIType:
    """Map OCEAN scores to the closest MBTI letters.

    E/I from extraversion, N/S from openness, F/T from agreeableness,
    J/P from conscientiousness.
    """
    e = "E" if b.extraversion >= 0.5 else "I"
    n = "N" if b.openness >= 0.5 else "S"
    f = "F" if b.agreeableness >= 0.5 else "T"
    j = "J" if b.conscientiousness >= 0.5 else "P"
    # MBTI conventional letter order is E/I, S/N, T/F, J/P
    return MBTIType(f"{e}{n}{f}{j}")


def _derive_traits(rng: RNG, b: BigFive, data: dict[str, Any]) -> list[str]:
    traits: list[str] = []
    if b.openness >= 0.65:
        traits += data["high_openness"]
    if b.conscientiousness >= 0.65:
        traits += data["high_conscientiousness"]
    if b.extraversion >= 0.65:
        traits += data["high_extraversion"]
    elif b.extraversion <= 0.35:
        traits += data["low_extraversion"]
    if b.agreeableness >= 0.65:
        traits += data["high_agreeableness"]
    elif b.agreeableness <= 0.35:
        traits += data["low_agreeableness"]
    if b.neuroticism >= 0.65:
        traits += data["high_neuroticism"]
    elif b.neuroticism <= 0.35:
        traits += data["low_neuroticism"]
    if not traits:
        traits = rng.weighted_sample(data["positive"], k=3)
    # de-duplicate while keeping order, cap at 5
    seen: list[str] = []
    for t in traits:
        if t not in seen:
            seen.append(t)
    return seen[:5]


register(PersonalityGenerator())
