"""Social / relationships generator: marital status, orientation, family.

Marital status is conditioned on age so the result is plausible; the minor
safety clamp also runs later in keylinks as a backstop.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.generators._helpers import as_enum, is_fixed, pick
from persona_factory.generators.base import Generator, register
from persona_factory.models.enums import MaritalStatus, SexualOrientation
from persona_factory.models.persona import Social

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG

_ORIENTATION_WEIGHTS = {
    SexualOrientation.HETEROSEXUAL: 0.89,
    SexualOrientation.BISEXUAL: 0.045,
    SexualOrientation.HOMOSEXUAL: 0.035,
    SexualOrientation.PANSEXUAL: 0.012,
    SexualOrientation.ASEXUAL: 0.01,
    SexualOrientation.QUEER: 0.005,
    SexualOrientation.QUESTIONING: 0.003,
}


def _marital_for_age(rng: RNG, age: int) -> MaritalStatus:
    if age < 18:
        return MaritalStatus.SINGLE
    if age < 25:
        return rng.weighted_choice(
            [MaritalStatus.SINGLE, MaritalStatus.IN_RELATIONSHIP, MaritalStatus.ENGAGED],
            [0.65, 0.3, 0.05],
        )
    if age < 40:
        return rng.weighted_choice(
            [
                MaritalStatus.SINGLE,
                MaritalStatus.IN_RELATIONSHIP,
                MaritalStatus.ENGAGED,
                MaritalStatus.MARRIED,
                MaritalStatus.DIVORCED,
            ],
            [0.28, 0.25, 0.1, 0.32, 0.05],
        )
    return rng.weighted_choice(
        [
            MaritalStatus.MARRIED,
            MaritalStatus.SINGLE,
            MaritalStatus.DIVORCED,
            MaritalStatus.WIDOWED,
            MaritalStatus.DOMESTIC_PARTNERSHIP,
        ],
        [0.55, 0.15, 0.18, 0.07, 0.05],
    )


class SocialGenerator(Generator):
    domain = "social"
    depends_on = ("identity",)

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        age = persona.identity.age or 30

        marital_fixed = is_fixed(config, "social.marital_status")
        if marital_fixed is not None:
            marital = MaritalStatus(marital_fixed)
        else:
            marital = _marital_for_age(rng, age)

        social = Social(
            marital_status=marital,
            sexual_orientation=as_enum(
                pick(
                    rng,
                    config,
                    "social.sexual_orientation",
                    list(_ORIENTATION_WEIGHTS),
                    list(_ORIENTATION_WEIGHTS.values()),
                ),
                SexualOrientation,
            ),
            siblings=rng.weighted_choice([0, 1, 2, 3, 4], [0.18, 0.4, 0.27, 0.1, 0.05]),
            social_circle_size=rng.choice(["small", "medium", "large"]),
        )

        # children: only for adults, more likely if married/older
        if age >= 22 and marital in {
            MaritalStatus.MARRIED,
            MaritalStatus.DIVORCED,
            MaritalStatus.WIDOWED,
            MaritalStatus.DOMESTIC_PARTNERSHIP,
        }:
            social.children = rng.weighted_choice([0, 1, 2, 3, 4], [0.25, 0.3, 0.28, 0.12, 0.05])
        else:
            social.children = 0 if age < 22 else rng.weighted_choice([0, 1], [0.8, 0.2])

        persona.social = social


register(SocialGenerator())
