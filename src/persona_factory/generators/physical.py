"""Physical attributes generator.

Height/weight are drawn from gender-conditioned Gaussians (in cm/kg) so the
numbers stay plausible; everything else samples from bundled lexicons.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.data import load_json
from persona_factory.generators._helpers import (
    as_enum,
    is_fixed,
    pick,
    pick_number,
    pick_sample,
)
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

# (mean_height_cm, sd, mean_bmi, bmi_sd) by gendered baseline. Weight is derived
# from height and a sampled BMI (weight = bmi * (h/100)**2) so the two cohere,
# rather than being drawn independently.
_MASC_STATS = (177.0, 7.0, 25.5, 3.8)
_FEM_STATS = (164.0, 6.5, 24.5, 4.2)
_NEUTRAL_STATS = (170.0, 8.0, 25.0, 4.0)

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
            h_mu, h_sd, bmi_mu, bmi_sd = _MASC_STATS
            masc = True
        elif gender in {Gender.FEMALE.value, Gender.TRANSGENDER_FEMALE.value}:
            h_mu, h_sd, bmi_mu, bmi_sd = _FEM_STATS
            masc = False
        else:
            h_mu, h_sd, bmi_mu, bmi_sd = _NEUTRAL_STATS
            masc = False

        height = pick_number(rng, config, "physical.height_cm", 140, 210, mu=h_mu, sigma=h_sd)
        # Weight is derived from height and a sampled BMI so the two cohere; an
        # explicit weight override still wins (and re-implies the BMI band).
        weight, bmi = _weight_and_bmi(rng, config, height, bmi_mu, bmi_sd)

        candidates, weights = _body_type_band(bmi, masc=masc)
        physical = Physical(
            height_cm=round(height, 1),
            weight_kg=round(weight, 1),
            body_type=as_enum(
                pick(rng, config, "physical.body_type", candidates, weights), BodyType
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


def _weight_and_bmi(
    rng: RNG,
    config: PersonaConfig,
    height_cm: float,
    bmi_mu: float,
    bmi_sd: float,
) -> tuple[float, float]:
    """Return ``(weight_kg, bmi)``, deriving weight from height and a sampled BMI.

    An explicit ``physical.weight_kg`` override is respected; the BMI is then
    back-computed from it so ``body_type`` still reflects the real numbers.
    """
    h_m = height_cm / 100.0
    if is_fixed(config, "physical.weight_kg") is not None:
        weight = pick_number(rng, config, "physical.weight_kg", 40, 160)
        bmi = weight / (h_m * h_m)
        return weight, bmi
    bmi = rng.bounded_gauss(bmi_mu, bmi_sd, 15.0, 45.0)
    weight = bmi * h_m * h_m
    weight = min(max(weight, 40.0), 160.0)
    return weight, weight / (h_m * h_m)


def _body_type_band(bmi: float, *, masc: bool) -> tuple[list[BodyType], list[float]]:
    """Map a BMI to a small weighted set of plausible body types.

    Muscular/curvy split by gender at the higher bands; the weighting keeps a
    little variety while ruling out contradictions (e.g. a lean BMI never reads
    as ``heavyset``).
    """
    if bmi < 18.5:
        return [BodyType.SLIM, BodyType.ATHLETIC], [0.8, 0.2]
    if bmi < 23.0:
        return [BodyType.SLIM, BodyType.ATHLETIC, BodyType.AVERAGE], [0.25, 0.35, 0.4]
    if bmi < 27.0:
        heavier = BodyType.MUSCULAR if masc else BodyType.CURVY
        return [BodyType.AVERAGE, BodyType.ATHLETIC, heavier], [0.5, 0.25, 0.25]
    if bmi < 32.0:
        heavier = BodyType.MUSCULAR if masc else BodyType.CURVY
        return [BodyType.AVERAGE, heavier, BodyType.HEAVYSET], [0.3, 0.35, 0.35]
    return [BodyType.HEAVYSET, BodyType.CURVY], [0.75, 0.25]


register(PhysicalGenerator())
