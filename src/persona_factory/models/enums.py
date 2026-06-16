"""Enumerations for the closed-set persona attributes.

Every enum is a ``str`` enum so values serialize to plain strings in JSON and
read naturally in rendered prompts (``Gender.FEMALE == "female"``).

These cover *categorical* attributes only. Open-ended fields (names, hobbies,
occupations, …) are plain strings backed by bundled data, not enums.
"""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """A string enum whose ``str()`` is its value (3.10-compatible)."""

    def __str__(self) -> str:  # pragma: no cover - trivial
        return str(self.value)


# --------------------------------------------------------------------------- #
# Identity / demographics
# --------------------------------------------------------------------------- #
class Gender(StrEnum):
    """Gender identity. Deliberately broad; extend via config if needed."""

    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    TRANSGENDER_MALE = "transgender_male"
    TRANSGENDER_FEMALE = "transgender_female"
    GENDERFLUID = "genderfluid"
    AGENDER = "agender"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class SexAssignedAtBirth(StrEnum):
    MALE = "male"
    FEMALE = "female"
    INTERSEX = "intersex"


class PronounSet(StrEnum):
    SHE_HER = "she/her"
    HE_HIM = "he/him"
    THEY_THEM = "they/them"
    XE_XEM = "xe/xem"
    ZE_ZIR = "ze/zir"
    IT_ITS = "it/its"


class Generation(StrEnum):
    """Western generational cohorts, keyed off birth year ranges."""

    GREATEST = "Greatest Generation"  # <=1927
    SILENT = "Silent Generation"  # 1928-1945
    BOOMER = "Baby Boomer"  # 1946-1964
    GEN_X = "Generation X"  # 1965-1980
    MILLENNIAL = "Millennial"  # 1981-1996
    GEN_Z = "Generation Z"  # 1997-2012
    GEN_ALPHA = "Generation Alpha"  # 2013+


class MaritalStatus(StrEnum):
    SINGLE = "single"
    IN_RELATIONSHIP = "in_relationship"
    ENGAGED = "engaged"
    MARRIED = "married"
    DOMESTIC_PARTNERSHIP = "domestic_partnership"
    SEPARATED = "separated"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class SexualOrientation(StrEnum):
    HETEROSEXUAL = "heterosexual"
    HOMOSEXUAL = "homosexual"
    BISEXUAL = "bisexual"
    PANSEXUAL = "pansexual"
    ASEXUAL = "asexual"
    QUEER = "queer"
    QUESTIONING = "questioning"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class LanguageProficiency(StrEnum):
    NATIVE = "native"
    FLUENT = "fluent"
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    BASIC = "basic"


# --------------------------------------------------------------------------- #
# Physical
# --------------------------------------------------------------------------- #
class BodyType(StrEnum):
    SLIM = "slim"
    ATHLETIC = "athletic"
    AVERAGE = "average"
    CURVY = "curvy"
    MUSCULAR = "muscular"
    HEAVYSET = "heavyset"


class Handedness(StrEnum):
    RIGHT = "right"
    LEFT = "left"
    AMBIDEXTROUS = "ambidextrous"


class BloodType(StrEnum):
    O_POS = "O+"
    O_NEG = "O-"
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"


# --------------------------------------------------------------------------- #
# Socioeconomic
# --------------------------------------------------------------------------- #
class EducationLevel(StrEnum):
    NONE = "none"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    HIGH_SCHOOL = "high_school"
    VOCATIONAL = "vocational"
    SOME_COLLEGE = "some_college"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    PROFESSIONAL = "professional"  # MD, JD, etc.


class EmploymentStatus(StrEnum):
    EMPLOYED_FULL_TIME = "employed_full_time"
    EMPLOYED_PART_TIME = "employed_part_time"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    STUDENT = "student"
    RETIRED = "retired"
    HOMEMAKER = "homemaker"
    UNABLE_TO_WORK = "unable_to_work"


class IncomeBand(StrEnum):
    """Coarse income tiers, locale-relative rather than absolute currency."""

    VERY_LOW = "very_low"
    LOW = "low"
    LOWER_MIDDLE = "lower_middle"
    MIDDLE = "middle"
    UPPER_MIDDLE = "upper_middle"
    HIGH = "high"
    VERY_HIGH = "very_high"


class SocialClass(StrEnum):
    WORKING = "working"
    LOWER_MIDDLE = "lower_middle"
    MIDDLE = "middle"
    UPPER_MIDDLE = "upper_middle"
    UPPER = "upper"


class Seniority(StrEnum):
    INTERN = "intern"
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


# --------------------------------------------------------------------------- #
# Personality frameworks
# --------------------------------------------------------------------------- #
class MBTIType(StrEnum):
    INTJ = "INTJ"
    INTP = "INTP"
    ENTJ = "ENTJ"
    ENTP = "ENTP"
    INFJ = "INFJ"
    INFP = "INFP"
    ENFJ = "ENFJ"
    ENFP = "ENFP"
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    ESTP = "ESTP"
    ESFP = "ESFP"


class EnneagramType(StrEnum):
    TYPE_1 = "1"  # Reformer
    TYPE_2 = "2"  # Helper
    TYPE_3 = "3"  # Achiever
    TYPE_4 = "4"  # Individualist
    TYPE_5 = "5"  # Investigator
    TYPE_6 = "6"  # Loyalist
    TYPE_7 = "7"  # Enthusiast
    TYPE_8 = "8"  # Challenger
    TYPE_9 = "9"  # Peacemaker


class DISCType(StrEnum):
    DOMINANCE = "D"
    INFLUENCE = "I"
    STEADINESS = "S"
    CONSCIENTIOUSNESS = "C"


class Temperament(StrEnum):
    """Keirsey temperaments."""

    ARTISAN = "artisan"
    GUARDIAN = "guardian"
    IDEALIST = "idealist"
    RATIONAL = "rational"


# --------------------------------------------------------------------------- #
# Beliefs & culture
# --------------------------------------------------------------------------- #
class Religion(StrEnum):
    CHRISTIANITY = "christianity"
    ISLAM = "islam"
    HINDUISM = "hinduism"
    BUDDHISM = "buddhism"
    JUDAISM = "judaism"
    SIKHISM = "sikhism"
    FOLK = "folk_religion"
    OTHER = "other"
    SPIRITUAL = "spiritual_not_religious"
    AGNOSTIC = "agnostic"
    ATHEIST = "atheist"
    NONE = "none"


class Religiosity(StrEnum):
    DEVOUT = "devout"
    PRACTICING = "practicing"
    OCCASIONAL = "occasional"
    CULTURAL = "cultural"
    NON_PRACTICING = "non_practicing"


class PoliticalOrientation(StrEnum):
    FAR_LEFT = "far_left"
    LEFT = "left"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    RIGHT = "right"
    FAR_RIGHT = "far_right"
    LIBERTARIAN = "libertarian"
    APOLITICAL = "apolitical"


# --------------------------------------------------------------------------- #
# Lifestyle / behavioral
# --------------------------------------------------------------------------- #
class Diet(StrEnum):
    OMNIVORE = "omnivore"
    FLEXITARIAN = "flexitarian"
    PESCATARIAN = "pescatarian"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    HALAL = "halal"
    KOSHER = "kosher"


class SubstanceUse(StrEnum):
    NEVER = "never"
    RARELY = "rarely"
    SOCIALLY = "socially"
    REGULARLY = "regularly"
    HEAVILY = "heavily"


class Chronotype(StrEnum):
    EARLY_BIRD = "early_bird"
    INTERMEDIATE = "intermediate"
    NIGHT_OWL = "night_owl"


class FitnessLevel(StrEnum):
    SEDENTARY = "sedentary"
    LIGHT = "lightly_active"
    MODERATE = "moderately_active"
    ACTIVE = "active"
    ATHLETE = "athlete"


class TechSavviness(StrEnum):
    LUDDITE = "luddite"
    BASIC = "basic"
    AVERAGE = "average"
    PROFICIENT = "proficient"
    EXPERT = "expert"


class SettlementType(StrEnum):
    URBAN = "urban"
    SUBURBAN = "suburban"
    RURAL = "rural"


# --------------------------------------------------------------------------- #
# Communication style
# --------------------------------------------------------------------------- #
class Formality(StrEnum):
    VERY_FORMAL = "very_formal"
    FORMAL = "formal"
    NEUTRAL = "neutral"
    CASUAL = "casual"
    VERY_CASUAL = "very_casual"


class Verbosity(StrEnum):
    TERSE = "terse"
    CONCISE = "concise"
    BALANCED = "balanced"
    VERBOSE = "verbose"
    RAMBLING = "rambling"


class HumorStyle(StrEnum):
    NONE = "none"
    DRY = "dry"
    WITTY = "witty"
    SARCASTIC = "sarcastic"
    SILLY = "silly"
    DARK = "dark"
    WHOLESOME = "wholesome"
    SELF_DEPRECATING = "self_deprecating"


class EmojiUsage(StrEnum):
    NONE = "none"
    RARE = "rare"
    MODERATE = "moderate"
    FREQUENT = "frequent"
    HEAVY = "heavy"


class Tone(StrEnum):
    WARM = "warm"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    PROFESSIONAL = "professional"
    BLUNT = "blunt"
    ENTHUSIASTIC = "enthusiastic"
    RESERVED = "reserved"
    EMPATHETIC = "empathetic"


class VocabularyLevel(StrEnum):
    SIMPLE = "simple"
    EVERYDAY = "everyday"
    ADVANCED = "advanced"
    TECHNICAL = "technical"
    ACADEMIC = "academic"
