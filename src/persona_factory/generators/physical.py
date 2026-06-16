"""Physical attributes generator.

Height/weight are drawn from gender-conditioned Gaussians (in cm/kg) so the
numbers stay plausible; everything else samples from bundled lexicons.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.data import load_json
from persona_factory.generators._helpers import as_enum, pick, pick_number, pick_sample
from persona_factory.generators.base import Generator, register
from persona_factory.models.enums import (
    BloodType,
    BodyType,
    Gender,
    Handedness,
)
from persona_factory.models.persona import Physical

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG

# (mean_height_cm, sd, mean_weight_kg, sd) by gendered body baseline.
_MASC_STATS = (177.0, 7.0, 79.0, 12.0)
_FEM_STATS = (164.0, 6.5, 67.0, 11.0)
_NEUTRAL_STATS = (170.0, 8.0, 73.0, 13.0)

_BLOOD_WEIGHTS = {
    BloodType.O_POS: 0.37,
    BloodType.A_POS: 0.31,
    BloodType.B_POS: 0.10,
    BloodType.O_NEG: 0.07,
    BloodType.A_NEG: 0.06,
    BloodType.AB_POS: 0.04,
    BloodType.B_NEG: 0.03,
    BloodType.AB_NEG: 0.02,
}
_HANDEDNESS_WEIGHTS = {
    Handedness.RIGHT: 0.89,
    Handedness.LEFT: 0.10,
    Handedness.AMBIDEXTROUS: 0.01,
}


class PhysicalGenerator(Generator):
    domain = "physical"
    depends_on = ("identity",)

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        lex = load_json("lexicons", "lifestyle.json")
        gender = persona.identity.gender

        if gender in {Gender.MALE.value, Gender.TRANSGENDER_MALE.value}:
            h_mu, h_sd, w_mu, w_sd = _MASC_STATS
        elif gender in {Gender.FEMALE.value, Gender.TRANSGENDER_FEMALE.value}:
            h_mu, h_sd, w_mu, w_sd = _FEM_STATS
        else:
            h_mu, h_sd, w_mu, w_sd = _NEUTRAL_STATS

        height = pick_number(
            rng, config, "physical.height_cm", 140, 210, mu=h_mu, sigma=h_sd
        )
        weight = pick_number(
            rng, config, "physical.weight_kg", 40, 160, mu=w_mu, sigma=w_sd
        )

        physical = Physical(
            height_cm=round(height, 1),
            weight_kg=round(weight, 1),
            body_type=as_enum(
                pick(rng, config, "physical.body_type", list(BodyType)), BodyType
            ),
            eye_color=pick(rng, config, "physical.eye_color", lex["eye_colors"]),
            hair_color=pick(rng, config, "physical.hair_color", lex["hair_colors"]),
            hair_style=pick(rng, config, "physical.hair_style", lex["hair_styles"]),
            skin_tone=pick(rng, config, "physical.skin_tone", lex["skin_tones"]),
            handedness=as_enum(
                pick(
                    rng,
                    config,
                    "physical.handedness",
                    list(_HANDEDNESS_WEIGHTS),
                    list(_HANDEDNESS_WEIGHTS.values()),
                ),
                Handedness,
            ),
            blood_type=as_enum(
                pick(
                    rng,
                    config,
                    "physical.blood_type",
                    list(_BLOOD_WEIGHTS),
                    list(_BLOOD_WEIGHTS.values()),
                ),
                BloodType,
            ),
            voice=pick(rng, config, "physical.voice", lex["voices"]),
        )
        # ~40% have a distinguishing feature.
        if rng.chance(0.4):
            physical.distinguishing_features = pick_sample(
                rng,
                config,
                "physical.distinguishing_features",
                lex["distinguishing_features"],
                k=rng.randint(1, 2),
            )
        persona.physical = physical




register(PhysicalGenerator())
