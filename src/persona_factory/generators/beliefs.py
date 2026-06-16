"""Beliefs / culture generator: religion, religiosity, politics, worldview."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.data import load_json
from persona_factory.generators._helpers import as_enum, pick
from persona_factory.generators.base import Generator, register
from persona_factory.models.enums import (
    PoliticalOrientation,
    Religion,
    Religiosity,
)
from persona_factory.models.persona import Beliefs

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG

_RELIGION_WEIGHTS = {
    Religion.CHRISTIANITY: 0.30,
    Religion.ISLAM: 0.18,
    Religion.NONE: 0.16,
    Religion.HINDUISM: 0.12,
    Religion.AGNOSTIC: 0.06,
    Religion.BUDDHISM: 0.05,
    Religion.ATHEIST: 0.05,
    Religion.SPIRITUAL: 0.04,
    Religion.JUDAISM: 0.02,
    Religion.SIKHISM: 0.01,
    Religion.FOLK: 0.005,
    Religion.OTHER: 0.005,
}
_NON_RELIGIOUS = {Religion.NONE, Religion.ATHEIST, Religion.AGNOSTIC}
_POLITICAL_WEIGHTS = {
    PoliticalOrientation.CENTER: 0.20,
    PoliticalOrientation.CENTER_LEFT: 0.18,
    PoliticalOrientation.CENTER_RIGHT: 0.18,
    PoliticalOrientation.LEFT: 0.13,
    PoliticalOrientation.RIGHT: 0.13,
    PoliticalOrientation.LIBERTARIAN: 0.06,
    PoliticalOrientation.APOLITICAL: 0.06,
    PoliticalOrientation.FAR_LEFT: 0.03,
    PoliticalOrientation.FAR_RIGHT: 0.03,
}


class BeliefsGenerator(Generator):
    domain = "beliefs"

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        values_lex = load_json("lexicons", "values.json")
        religion = pick(
            rng,
            config,
            "beliefs.religion",
            list(_RELIGION_WEIGHTS),
            list(_RELIGION_WEIGHTS.values()),
        )
        religion = religion if isinstance(religion, Religion) else Religion(religion)

        beliefs = Beliefs(
            religion=religion,
            political_orientation=as_enum(
                pick(
                    rng,
                    config,
                    "beliefs.political_orientation",
                    list(_POLITICAL_WEIGHTS),
                    list(_POLITICAL_WEIGHTS.values()),
                ),
                PoliticalOrientation,
            ),
            worldview=pick(rng, config, "beliefs.worldview", values_lex["worldviews"]),
        )
        # religiosity only meaningful for religious personas
        if religion not in _NON_RELIGIOUS:
            beliefs.religiosity = as_enum(
                pick(rng, config, "beliefs.religiosity", list(Religiosity)),
                Religiosity,
            )
        persona.beliefs = beliefs


register(BeliefsGenerator())
