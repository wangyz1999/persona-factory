"""Tests for the identity generator and intra-identity key-links."""

from __future__ import annotations

import datetime as _dt

import pytest

from persona_factory.data import available_locales, load_locale
from persona_factory.factory import PersonaFactory
from persona_factory.generators.identity import generation_for_year
from persona_factory.models.enums import Gender, PronounSet


def test_generates_complete_identity(factory: PersonaFactory) -> None:
    p = factory.generate()
    ident = p.identity
    assert ident.given_name and ident.family_name
    assert ident.full_name
    assert ident.gender is not None
    assert ident.age is not None
    assert ident.date_of_birth is not None
    assert ident.generation is not None


def test_reproducible_with_same_seed() -> None:
    a = PersonaFactory("en_US", seed=42).generate()
    b = PersonaFactory("en_US", seed=42).generate()
    assert a.to_json() == b.to_json()


def test_different_seeds_differ() -> None:
    a = PersonaFactory("en_US", seed=1).generate()
    b = PersonaFactory("en_US", seed=2).generate()
    assert a.to_json() != b.to_json()


def test_gender_override_is_honored(factory: PersonaFactory) -> None:
    p = factory.generate(gender="female")
    assert p.identity.gender == Gender.FEMALE.value


def test_age_override_is_honored(factory: PersonaFactory) -> None:
    p = factory.generate(age=42)
    assert p.identity.age == 42


def test_age_range_override(factory: PersonaFactory) -> None:
    for _ in range(20):
        p = factory.generate(age_range=(25, 30))
        assert 25 <= p.identity.age <= 30


def test_pronouns_follow_gender() -> None:
    f = PersonaFactory("en_US", seed=3)
    assert f.generate(gender="male").identity.pronouns == PronounSet.HE_HIM.value
    assert f.generate(gender="female").identity.pronouns == PronounSet.SHE_HER.value


def test_pronoun_override() -> None:
    f = PersonaFactory("en_US", seed=3)
    p = f.generate(gender="female", pronouns="they/them")
    assert p.identity.pronouns == PronounSet.THEY_THEM.value


def test_dob_matches_age() -> None:
    p = PersonaFactory("en_US", seed=11).generate(age=40)
    # reference year is 2025
    assert p.identity.date_of_birth.year == 2025 - 40


def test_generation_boundaries() -> None:
    assert generation_for_year(1925).value == "Greatest Generation"
    assert generation_for_year(1990).value == "Millennial"
    assert generation_for_year(2000).value == "Generation Z"
    assert generation_for_year(2015).value == "Generation Alpha"


@pytest.mark.parametrize("locale", list(available_locales()))
def test_name_drawn_from_locale_pool(locale: str) -> None:
    data = load_locale(locale, "data.json")
    p = PersonaFactory(locale, seed=5).generate(gender="male")
    valid_given = set(data["given_names"]["male"] + data["given_names"].get("unisex", []))
    assert p.identity.given_name in valid_given
    assert p.identity.family_name in set(data["surnames"])


def test_family_first_name_order() -> None:
    p = PersonaFactory("ja_JP", seed=8).generate()
    # full name should be family + given concatenated, no space
    assert p.identity.full_name == f"{p.identity.family_name}{p.identity.given_name}"


def test_dob_is_a_date() -> None:
    p = PersonaFactory("en_US", seed=1).generate()
    assert isinstance(p.identity.date_of_birth, _dt.date)
