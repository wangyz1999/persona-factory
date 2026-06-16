"""Tests for the non-identity domain generators."""

from __future__ import annotations

from persona_factory.config import ALL_DOMAINS
from persona_factory.factory import PersonaFactory
from persona_factory.models.enums import MBTIType


def _full(seed: int = 1) -> object:
    f = PersonaFactory("en_US", seed=seed)
    return f.generate(include=list(ALL_DOMAINS))


def test_all_domains_populate() -> None:
    p = _full()
    for domain in ALL_DOMAINS:
        assert getattr(p, domain) is not None, f"{domain} not generated"


def test_physical_ranges() -> None:
    p = _full(2)
    assert 140 <= p.physical.height_cm <= 210
    assert 40 <= p.physical.weight_kg <= 160
    assert p.physical.eye_color


def test_socioeconomic_experience_bounded_by_age() -> None:
    for seed in range(10):
        p = PersonaFactory("en_US", seed=seed).generate(
            age=25, include=["identity", "socioeconomic"]
        )
        assert p.socioeconomic.years_experience <= 25 - 18


def test_personality_mbti_derived_from_ocean() -> None:
    p = _full(3)
    b = p.personality.big_five
    mbti = p.personality.mbti
    assert isinstance(MBTIType(mbti), MBTIType)
    # check E/I letter matches extraversion
    assert mbti[0] == ("E" if b.extraversion >= 0.5 else "I")


def test_mbti_override_pins_value() -> None:
    p = PersonaFactory("en_US", seed=1).generate(
        mbti="INTJ", include=["personality"]
    )
    assert p.personality.mbti == "INTJ"


def test_contact_email_derives_from_name() -> None:
    p = PersonaFactory("en_US", seed=1).generate(
        given_name="Ada", family_name="Lovelace", include=["identity", "contact"]
    )
    assert "ada" in p.contact.email.lower()


def test_contact_handles_non_latin_names() -> None:
    # Japanese names ASCII-fold to empty; generator must not crash
    p = PersonaFactory("ja_JP", seed=1).generate(include=["identity", "contact"])
    assert p.contact.email
    assert "@" in p.contact.email


def test_beliefs_religiosity_only_when_religious() -> None:
    p = PersonaFactory("en_US", seed=1).generate(
        religion="atheist", include=["beliefs"]
    )
    assert p.beliefs.religiosity is None


def test_location_postal_matches_mask_length() -> None:
    p = PersonaFactory("en_US", seed=1).generate(include=["location"])
    # en_US mask is ##### -> 5 digits
    assert len(p.location.postal_code) == 5
    assert p.location.postal_code.isdigit()


def test_documents_card_passes_luhn() -> None:
    p = PersonaFactory("en_US", seed=1).generate(include=["documents"])
    digits = [int(c) for c in p.documents.credit_card if c.isdigit()][::-1]
    total = 0
    for i, d in enumerate(digits):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    assert total % 10 == 0


def test_documents_marked_fake() -> None:
    p = PersonaFactory("en_US", seed=1).generate(include=["documents"])
    assert p.documents.national_id.startswith("FAKE")
    assert p.documents.passport_number.startswith("FAKE")


def test_full_persona_reproducible() -> None:
    a = _full(7)
    b = _full(7)
    assert a.to_json() == b.to_json()


def test_narrative_bio_mentions_name() -> None:
    p = PersonaFactory("en_US", seed=1).generate(
        given_name="Ada", include=list(ALL_DOMAINS)
    )
    assert "Ada" in p.narrative.bio
