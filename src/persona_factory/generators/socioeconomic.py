"""Socioeconomic generator: occupation, education, employment, income.

Occupation is sampled from the bundled industry taxonomy. Education and income
are sampled here; the occupation->income sanity clamp lives in
:mod:`persona_factory.keylinks` so it can see the final occupation/status.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.data import load_json
from persona_factory.generators._helpers import as_enum, is_fixed, pick, pick_number
from persona_factory.generators.base import Generator, register
from persona_factory.models.enums import (
    EducationLevel,
    EmploymentStatus,
    IncomeBand,
    Seniority,
    SocialClass,
)
from persona_factory.models.persona import Socioeconomic

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG

_EDUCATION_WEIGHTS = {
    EducationLevel.HIGH_SCHOOL: 0.28,
    EducationLevel.SOME_COLLEGE: 0.15,
    EducationLevel.VOCATIONAL: 0.08,
    EducationLevel.ASSOCIATE: 0.10,
    EducationLevel.BACHELOR: 0.23,
    EducationLevel.MASTER: 0.11,
    EducationLevel.DOCTORATE: 0.02,
    EducationLevel.PROFESSIONAL: 0.03,
}
_SENIORITY_BY_EXPERIENCE = [
    (0, Seniority.INTERN),
    (1, Seniority.ENTRY),
    (3, Seniority.JUNIOR),
    (6, Seniority.MID),
    (10, Seniority.SENIOR),
    (15, Seniority.LEAD),
    (20, Seniority.MANAGER),
]


class SocioeconomicGenerator(Generator):
    domain = "socioeconomic"
    depends_on = ("identity",)

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        taxonomy = load_json("occupations", "taxonomy.json")
        age = persona.identity.age or 30

        # -- industry + occupation --------------------------------------
        industries = list(taxonomy["industries"].keys())
        industry = pick(rng, config, "socioeconomic.industry", industries)
        occupation = pick(
            rng,
            config,
            "socioeconomic.occupation",
            taxonomy["industries"][industry],
        )

        # -- education ---------------------------------------------------
        education = pick(
            rng,
            config,
            "socioeconomic.education_level",
            list(_EDUCATION_WEIGHTS),
            list(_EDUCATION_WEIGHTS.values()),
        )
        education = as_enum(education, EducationLevel)

        employment_fixed = is_fixed(config, "socioeconomic.employment_status")
        employment = (
            EmploymentStatus(employment_fixed)
            if employment_fixed is not None
            else EmploymentStatus.EMPLOYED_FULL_TIME
        )

        socio = Socioeconomic(
            industry=industry,
            occupation=occupation,
            job_title=occupation,
            education_level=education,
            employment_status=employment,
            social_class=as_enum(
                pick(rng, config, "socioeconomic.social_class", list(SocialClass)),
                SocialClass,
            ),
        )

        # field of study only meaningful for tertiary education
        if education in {
            EducationLevel.ASSOCIATE,
            EducationLevel.BACHELOR,
            EducationLevel.MASTER,
            EducationLevel.DOCTORATE,
            EducationLevel.PROFESSIONAL,
        }:
            socio.field_of_study = pick(
                rng,
                config,
                "socioeconomic.field_of_study",
                taxonomy["fields_of_study"],
            )

        # -- experience + seniority (bounded by age) --------------------
        max_exp = max(0, age - 18)
        years = int(
            pick_number(rng, config, "socioeconomic.years_experience", 0, max_exp, integer=True)
        )
        socio.years_experience = years
        socio.seniority = _seniority_for(years)

        # -- income band (provisional; keylinks may clamp) --------------
        if is_fixed(config, "socioeconomic.income_band") is not None:
            socio.income_band = as_enum(is_fixed(config, "socioeconomic.income_band"), IncomeBand)
        else:
            socio.income_band = _income_for_education(rng, education)

        persona.socioeconomic = socio


def _seniority_for(years: int) -> Seniority:
    result = Seniority.INTERN
    for threshold, level in _SENIORITY_BY_EXPERIENCE:
        if years >= threshold:
            result = level
    return result


def _income_for_education(rng: RNG, education: EducationLevel) -> IncomeBand:
    higher = {
        EducationLevel.MASTER,
        EducationLevel.DOCTORATE,
        EducationLevel.PROFESSIONAL,
    }
    if education in higher:
        return rng.weighted_choice(
            [IncomeBand.MIDDLE, IncomeBand.UPPER_MIDDLE, IncomeBand.HIGH],
            [0.3, 0.4, 0.3],
        )
    if education == EducationLevel.BACHELOR:
        return rng.weighted_choice(
            [IncomeBand.LOWER_MIDDLE, IncomeBand.MIDDLE, IncomeBand.UPPER_MIDDLE],
            [0.3, 0.4, 0.3],
        )
    return rng.weighted_choice(
        [IncomeBand.LOW, IncomeBand.LOWER_MIDDLE, IncomeBand.MIDDLE],
        [0.3, 0.4, 0.3],
    )


register(SocioeconomicGenerator())
