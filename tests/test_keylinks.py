"""Tests for cross-domain key-link resolvers."""

from __future__ import annotations

from persona_factory.factory import PersonaFactory


def test_high_income_occupation_clamped_up() -> None:
    p = PersonaFactory("en_US", seed=1).generate(
        occupation="Surgeon", age=45, include=["identity", "socioeconomic"]
    )
    assert p.socioeconomic.income_band in {"upper_middle", "high", "very_high"}


def test_student_age_sets_employment_and_low_income() -> None:
    p = PersonaFactory("en_US", seed=2).generate(
        age=19, include=["identity", "socioeconomic"]
    )
    assert p.socioeconomic.employment_status == "student"
    assert p.socioeconomic.income_band in {"very_low", "low", "lower_middle"}


def test_retirement_age() -> None:
    p = PersonaFactory("en_US", seed=2).generate(
        age=70, include=["identity", "socioeconomic"]
    )
    assert p.socioeconomic.employment_status == "retired"


def test_minor_is_single_no_children() -> None:
    p = PersonaFactory("en_US", seed=3).generate(
        age=15, include=["identity", "social"]
    )
    assert p.social.marital_status == "single"
    assert p.social.children == 0


def test_currency_follows_locale() -> None:
    p = PersonaFactory("ja_JP", seed=4).generate(include=["socioeconomic"])
    assert p.socioeconomic.currency == "JPY"


def test_explicit_income_not_overridden() -> None:
    p = PersonaFactory("en_US", seed=5).generate(
        occupation="Surgeon", income_band="low", include=["identity", "socioeconomic"]
    )
    assert p.socioeconomic.income_band == "low"
