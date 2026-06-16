"""The :class:`Persona` data model and its nested per-domain sub-models.

Design rules:

* Every field is **optional** (defaults to ``None`` or an empty collection) so a
  caller can request any subset of attributes without tripping validation.
* Sub-models mirror the attribute taxonomy, one per attribute domain.
* Models are pydantic v2, so ``.model_dump()``, ``.model_dump_json()`` and JSON
  schema export all come for free. Rendering helpers live in
  :mod:`persona_factory.rendering` and are attached as thin methods here.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from persona_factory.models.enums import (
    BloodType,
    BodyType,
    Chronotype,
    Diet,
    DISCType,
    EducationLevel,
    EmojiUsage,
    EmploymentStatus,
    EnneagramType,
    FitnessLevel,
    Formality,
    Gender,
    Generation,
    Handedness,
    HumorStyle,
    IncomeBand,
    LanguageProficiency,
    MaritalStatus,
    MBTIType,
    PoliticalOrientation,
    PronounSet,
    Religion,
    Religiosity,
    Seniority,
    SettlementType,
    SexAssignedAtBirth,
    SexualOrientation,
    SocialClass,
    SubstanceUse,
    TechSavviness,
    Temperament,
    Tone,
    Verbosity,
    VocabularyLevel,
)


class _Base(BaseModel):
    """Shared config for every persona sub-model."""

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",  # let custom generators attach extra fields
    )


# --------------------------------------------------------------------------- #
# A. Identity / demographics
# --------------------------------------------------------------------------- #
class SpokenLanguage(_Base):
    language: str
    proficiency: LanguageProficiency | None = None


class Identity(_Base):
    given_name: str | None = None
    middle_name: str | None = None
    family_name: str | None = None
    full_name: str | None = None
    nickname: str | None = None
    prefix: str | None = None
    suffix: str | None = None

    gender: Gender | None = None
    sex_assigned_at_birth: SexAssignedAtBirth | None = None
    pronouns: PronounSet | None = None

    age: int | None = Field(default=None, ge=0, le=120)
    date_of_birth: _dt.date | None = None
    generation: Generation | None = None

    nationality: str | None = None
    ethnicity: str | None = None
    ancestry: list[str] = Field(default_factory=list)

    native_language: str | None = None
    spoken_languages: list[SpokenLanguage] = Field(default_factory=list)
    locale: str | None = None
    script: str | None = None


# --------------------------------------------------------------------------- #
# B. Physical
# --------------------------------------------------------------------------- #
class Physical(_Base):
    height_cm: float | None = Field(default=None, ge=30, le=260)
    weight_kg: float | None = Field(default=None, ge=2, le=400)
    body_type: BodyType | None = None
    eye_color: str | None = None
    hair_color: str | None = None
    hair_style: str | None = None
    skin_tone: str | None = None
    handedness: Handedness | None = None
    blood_type: BloodType | None = None
    disabilities: list[str] = Field(default_factory=list)
    distinguishing_features: list[str] = Field(default_factory=list)
    voice: str | None = None


# --------------------------------------------------------------------------- #
# C. Contact / digital
# --------------------------------------------------------------------------- #
class SocialProfile(_Base):
    platform: str
    handle: str
    url: str | None = None


class Contact(_Base):
    email: str | None = None
    phone: str | None = None
    username: str | None = None
    password: str | None = None  # synthetic only
    social_profiles: list[SocialProfile] = Field(default_factory=list)
    ip_address: str | None = None
    user_agent: str | None = None
    device: str | None = None
    avatar_seed: str | None = None


# --------------------------------------------------------------------------- #
# D. Location / geography
# --------------------------------------------------------------------------- #
class Location(_Base):
    street_address: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    country_code: str | None = None
    postal_code: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    timezone: str | None = None
    settlement_type: SettlementType | None = None


# --------------------------------------------------------------------------- #
# E. Socioeconomic
# --------------------------------------------------------------------------- #
class Socioeconomic(_Base):
    occupation: str | None = None
    job_title: str | None = None
    industry: str | None = None
    employer: str | None = None
    seniority: Seniority | None = None
    years_experience: int | None = Field(default=None, ge=0, le=80)
    employment_status: EmploymentStatus | None = None
    education_level: EducationLevel | None = None
    field_of_study: str | None = None
    institution: str | None = None
    income_band: IncomeBand | None = None
    annual_income: int | None = Field(default=None, ge=0)
    currency: str | None = None
    social_class: SocialClass | None = None


# --------------------------------------------------------------------------- #
# F. Personality (multi-framework)
# --------------------------------------------------------------------------- #
class BigFive(_Base):
    """OCEAN scores in ``[0, 1]`` plus a coarse label per trait."""

    openness: float = Field(ge=0, le=1)
    conscientiousness: float = Field(ge=0, le=1)
    extraversion: float = Field(ge=0, le=1)
    agreeableness: float = Field(ge=0, le=1)
    neuroticism: float = Field(ge=0, le=1)


class Personality(_Base):
    big_five: BigFive | None = None
    mbti: MBTIType | None = None
    enneagram_type: EnneagramType | None = None
    enneagram_wing: str | None = None
    disc: DISCType | None = None
    hexaco_honesty_humility: float | None = Field(default=None, ge=0, le=1)
    temperament: Temperament | None = None
    traits: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# G. Values & character
# --------------------------------------------------------------------------- #
class Values(_Base):
    core_values: list[str] = Field(default_factory=list)
    moral_foundations: list[str] = Field(default_factory=list)
    character_strengths: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# H. Beliefs / culture
# --------------------------------------------------------------------------- #
class Beliefs(_Base):
    religion: Religion | None = None
    religiosity: Religiosity | None = None
    political_orientation: PoliticalOrientation | None = None
    worldview: str | None = None


# --------------------------------------------------------------------------- #
# I. Lifestyle / behavioral
# --------------------------------------------------------------------------- #
class Lifestyle(_Base):
    hobbies: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    diet: Diet | None = None
    allergies: list[str] = Field(default_factory=list)
    fitness_level: FitnessLevel | None = None
    smoking: SubstanceUse | None = None
    alcohol: SubstanceUse | None = None
    chronotype: Chronotype | None = None
    favorite_media: list[str] = Field(default_factory=list)
    favorite_brands: list[str] = Field(default_factory=list)
    tech_savviness: TechSavviness | None = None


# --------------------------------------------------------------------------- #
# J. Social / relationships
# --------------------------------------------------------------------------- #
class Social(_Base):
    marital_status: MaritalStatus | None = None
    sexual_orientation: SexualOrientation | None = None
    children: int | None = Field(default=None, ge=0, le=20)
    siblings: int | None = Field(default=None, ge=0, le=20)
    living_with: str | None = None
    social_circle_size: str | None = None


# --------------------------------------------------------------------------- #
# K. Communication style
# --------------------------------------------------------------------------- #
class CommunicationStyle(_Base):
    tone: Tone | None = None
    formality: Formality | None = None
    verbosity: Verbosity | None = None
    vocabulary_level: VocabularyLevel | None = None
    humor: HumorStyle | None = None
    emoji_usage: EmojiUsage | None = None
    accent: str | None = None
    dialect: str | None = None
    catchphrases: list[str] = Field(default_factory=list)
    typing_quirks: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# L. Narrative / psychology
# --------------------------------------------------------------------------- #
class Narrative(_Base):
    goals: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    motivations: list[str] = Field(default_factory=list)
    secrets: list[str] = Field(default_factory=list)
    pet_peeves: list[str] = Field(default_factory=list)
    quirks: list[str] = Field(default_factory=list)
    life_events: list[str] = Field(default_factory=list)
    bio: str | None = None
    backstory: str | None = None
    sample_dialogue: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# M. Synthetic identity documents (clearly fake)
# --------------------------------------------------------------------------- #
class Documents(_Base):
    national_id: str | None = None
    credit_card: str | None = None
    iban: str | None = None
    license_plate: str | None = None
    passport_number: str | None = None


# --------------------------------------------------------------------------- #
# Root model
# --------------------------------------------------------------------------- #
class Persona(_Base):
    """A complete synthetic person. All domains are optional sub-models."""

    identity: Identity = Field(default_factory=Identity)
    physical: Physical | None = None
    contact: Contact | None = None
    location: Location | None = None
    socioeconomic: Socioeconomic | None = None
    personality: Personality | None = None
    values: Values | None = None
    beliefs: Beliefs | None = None
    lifestyle: Lifestyle | None = None
    social: Social | None = None
    communication: CommunicationStyle | None = None
    narrative: Narrative | None = None
    documents: Documents | None = None

    # provenance: the seed/locale that produced this persona, for reproducibility
    meta: dict[str, Any] = Field(default_factory=dict)

    # -- convenience -----------------------------------------------------
    @property
    def display_name(self) -> str:
        """Best available human name, falling back gracefully."""
        if self.identity.full_name:
            return self.identity.full_name
        parts = [self.identity.given_name, self.identity.family_name]
        name = " ".join(p for p in parts if p)
        return name or self.identity.nickname or "Unnamed Persona"

    # -- rendering (thin wrappers around persona_factory.rendering) ------
    def to_dict(self, *, exclude_none: bool = True) -> dict[str, Any]:
        return self.model_dump(exclude_none=exclude_none, mode="json")

    def to_json(self, *, exclude_none: bool = True, indent: int | None = 2) -> str:
        return self.model_dump_json(exclude_none=exclude_none, indent=indent)

    def to_system_prompt(self, **kwargs: Any) -> str:
        """Render as a second-person LLM system prompt."""
        from persona_factory.rendering.system_prompt import render_system_prompt

        return render_system_prompt(self, **kwargs)

    def to_markdown_card(self, **kwargs: Any) -> str:
        """Render as a human-readable markdown persona card."""
        from persona_factory.rendering.card import render_card

        return render_card(self, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - convenience
        return f"Persona({self.display_name})"
