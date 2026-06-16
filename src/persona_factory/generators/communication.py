"""Communication style generator.

When personality is present, tone/verbosity/formality are nudged by the OCEAN
profile (extraverts skew enthusiastic & verbose; high-conscientiousness skews
formal) so the speaking style matches the inner traits. Otherwise everything is
sampled uniformly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.data import load_json
from persona_factory.generators._helpers import as_enum, is_fixed, pick, pick_sample
from persona_factory.generators.base import Generator, register
from persona_factory.models.enums import (
    EmojiUsage,
    Formality,
    HumorStyle,
    Tone,
    Verbosity,
    VocabularyLevel,
)
from persona_factory.models.persona import CommunicationStyle

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import BigFive, Persona
    from persona_factory.rng import RNG


class CommunicationGenerator(Generator):
    domain = "communication"
    depends_on = ("personality",)

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        lex = load_json("lexicons", "communication.json")
        big_five = persona.personality.big_five if persona.personality else None

        comm = CommunicationStyle(
            tone=self._tone(rng, config, big_five),
            formality=self._formality(rng, config, big_five),
            verbosity=self._verbosity(rng, config, big_five),
            vocabulary_level=as_enum(
                pick(rng, config, "communication.vocabulary_level", list(VocabularyLevel)),
                VocabularyLevel,
            ),
            humor=as_enum(
                pick(rng, config, "communication.humor", list(HumorStyle)), HumorStyle
            ),
            emoji_usage=as_enum(
                pick(rng, config, "communication.emoji_usage", list(EmojiUsage)),
                EmojiUsage,
            ),
            accent=pick(rng, config, "communication.accent", lex["accents"]),
            dialect=pick(rng, config, "communication.dialect", lex["dialects"]),
        )
        if rng.chance(0.5):
            comm.catchphrases = pick_sample(
                rng, config, "communication.catchphrases", lex["catchphrases"], k=rng.randint(1, 2)
            )
        if rng.chance(0.4):
            comm.typing_quirks = pick_sample(
                rng, config, "communication.typing_quirks", lex["typing_quirks"], k=1
            )
        persona.communication = comm

    def _tone(
        self, rng: RNG, config: PersonaConfig, big_five: BigFive | None
    ) -> Tone:
        if is_fixed(config, "communication.tone") is not None or big_five is None:
            return as_enum(pick(rng, config, "communication.tone", list(Tone)), Tone)
        if big_five.extraversion >= 0.65:
            return rng.choice([Tone.ENTHUSIASTIC, Tone.FRIENDLY, Tone.WARM])
        if big_five.extraversion <= 0.35:
            return rng.choice([Tone.RESERVED, Tone.NEUTRAL, Tone.PROFESSIONAL])
        if big_five.agreeableness >= 0.65:
            return rng.choice([Tone.WARM, Tone.EMPATHETIC, Tone.FRIENDLY])
        return as_enum(pick(rng, config, "communication.tone", list(Tone)), Tone)

    def _formality(
        self, rng: RNG, config: PersonaConfig, big_five: BigFive | None
    ) -> Formality:
        if is_fixed(config, "communication.formality") is not None or big_five is None:
            return as_enum(
                pick(rng, config, "communication.formality", list(Formality)), Formality
            )
        if big_five.conscientiousness >= 0.65:
            return rng.choice([Formality.FORMAL, Formality.NEUTRAL])
        if big_five.conscientiousness <= 0.35:
            return rng.choice([Formality.CASUAL, Formality.VERY_CASUAL])
        return as_enum(
            pick(rng, config, "communication.formality", list(Formality)), Formality
        )

    def _verbosity(
        self, rng: RNG, config: PersonaConfig, big_five: BigFive | None
    ) -> Verbosity:
        if is_fixed(config, "communication.verbosity") is not None or big_five is None:
            return as_enum(
                pick(rng, config, "communication.verbosity", list(Verbosity)), Verbosity
            )
        if big_five.extraversion >= 0.65:
            return rng.choice([Verbosity.VERBOSE, Verbosity.BALANCED, Verbosity.RAMBLING])
        if big_five.extraversion <= 0.35:
            return rng.choice([Verbosity.TERSE, Verbosity.CONCISE])
        return as_enum(
            pick(rng, config, "communication.verbosity", list(Verbosity)), Verbosity
        )




register(CommunicationGenerator())
