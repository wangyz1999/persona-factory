"""Identity / demographics generator.

This generator owns the *intra-identity* key-links:

* ``gender + locale -> given/family name`` (name pools are gender- & locale-
  partitioned; locales with ``name_order == "family_first"`` order the full
  name accordingly),
* ``gender -> pronouns`` (overridable),
* ``age -> date_of_birth -> generation``,
* ``locale -> nationality / language / script``.
"""

from __future__ import annotations

import datetime as _dt
from typing import TYPE_CHECKING, Any

from persona_factory.generators._helpers import is_fixed, pick, pick_number
from persona_factory.generators.base import Generator, register
from persona_factory.models.enums import (
    Gender,
    Generation,
    LanguageProficiency,
    PronounSet,
)
from persona_factory.models.persona import Identity, SpokenLanguage

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG

# Default reference "today" for age<->DOB math. Fixed so personas are
# reproducible and do not silently drift as the wall clock advances (the RNG ban
# on Date.now() applies in spirit here too). Callers can override it per-config
# via ``PersonaConfig.reference_year`` to keep ages current.
_REFERENCE_YEAR = 2025

_GENDER_WEIGHTS = {
    Gender.MALE: 0.49,
    Gender.FEMALE: 0.49,
    Gender.NON_BINARY: 0.012,
    Gender.TRANSGENDER_MALE: 0.003,
    Gender.TRANSGENDER_FEMALE: 0.003,
    Gender.GENDERFLUID: 0.001,
    Gender.AGENDER: 0.001,
}

# Which name pool to draw from for each gender.
_MASC = {Gender.MALE, Gender.TRANSGENDER_MALE}
_FEM = {Gender.FEMALE, Gender.TRANSGENDER_FEMALE}

_DEFAULT_PRONOUNS = {
    Gender.MALE: PronounSet.HE_HIM,
    Gender.FEMALE: PronounSet.SHE_HER,
    Gender.TRANSGENDER_MALE: PronounSet.HE_HIM,
    Gender.TRANSGENDER_FEMALE: PronounSet.SHE_HER,
}


def generation_for_year(birth_year: int) -> Generation:
    """Map a birth year to its Western generational cohort."""
    if birth_year <= 1927:
        return Generation.GREATEST
    if birth_year <= 1945:
        return Generation.SILENT
    if birth_year <= 1964:
        return Generation.BOOMER
    if birth_year <= 1980:
        return Generation.GEN_X
    if birth_year <= 1996:
        return Generation.MILLENNIAL
    if birth_year <= 2012:
        return Generation.GEN_Z
    return Generation.GEN_ALPHA


class IdentityGenerator(Generator):
    domain = "identity"

    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict[str, Any],
    ) -> None:
        identity = persona.identity

        # -- gender ------------------------------------------------------
        genders = list(_GENDER_WEIGHTS.keys())
        weights = list(_GENDER_WEIGHTS.values())
        gender = pick(rng, config, "identity.gender", genders, weights)
        if isinstance(gender, str):
            gender = Gender(gender)
        identity.gender = gender

        # -- name (depends on gender + locale) ---------------------------
        names = locale_data["given_names"]
        if gender in _MASC:
            pool = names.get("male", []) + names.get("unisex", [])
        elif gender in _FEM:
            pool = names.get("female", []) + names.get("unisex", [])
        else:
            pool = names.get("male", []) + names.get("female", []) + names.get("unisex", [])
        identity.given_name = pick(rng, config, "identity.given_name", pool)
        identity.family_name = pick(rng, config, "identity.family_name", locale_data["surnames"])
        # ~30% of personas get a middle name (same gendered pool).
        if rng.chance(0.3):
            identity.middle_name = rng.choice(pool)

        family_first = locale_data.get("name_order") == "family_first"
        if family_first:
            identity.full_name = f"{identity.family_name}{identity.given_name}"
        else:
            identity.full_name = f"{identity.given_name} {identity.family_name}"

        # -- pronouns (depends on gender, overridable) -------------------
        pronoun_override = is_fixed(config, "identity.pronouns")
        if pronoun_override is not None:
            identity.pronouns = PronounSet(pronoun_override)
        else:
            identity.pronouns = _DEFAULT_PRONOUNS.get(gender, PronounSet.THEY_THEM)

        # -- age -> DOB -> generation ------------------------------------
        age = int(pick_number(rng, config, "identity.age", 18, 80, integer=True, mu=38, sigma=16))
        identity.age = age
        reference_year = getattr(config, "reference_year", _REFERENCE_YEAR)
        birth_year = reference_year - age
        month = rng.randint(1, 12)
        # keep day valid for every month
        day = rng.randint(1, 28)
        identity.date_of_birth = _dt.date(birth_year, month, day)
        identity.generation = generation_for_year(birth_year)

        # -- locale-derived demographics ---------------------------------
        identity.locale = config.locale
        identity.script = locale_data.get("script")
        identity.nationality = locale_data.get("country")
        language = locale_data.get("language")
        identity.native_language = language
        if language:
            identity.spoken_languages = [
                SpokenLanguage(language=language, proficiency=LanguageProficiency.NATIVE)
            ]
            # Many non-English locales also speak English at varying levels.
            if language != "English" and rng.chance(0.5):
                identity.spoken_languages.append(
                    SpokenLanguage(
                        language="English",
                        proficiency=rng.choice(
                            [
                                LanguageProficiency.BASIC,
                                LanguageProficiency.CONVERSATIONAL,
                                LanguageProficiency.PROFESSIONAL,
                            ]
                        ),
                    )
                )

        persona.identity = Identity.model_validate(identity.model_dump())


register(IdentityGenerator())
