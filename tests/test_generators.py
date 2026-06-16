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
    p = PersonaFactory("en_US", seed=1).generate(mbti="INTJ", include=["personality"])
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
    p = PersonaFactory("en_US", seed=1).generate(religion="atheist", include=["beliefs"])
    assert p.beliefs.religiosity is None


def test_location_postal_matches_mask_length() -> None:
    p = PersonaFactory("en_US", seed=1).generate(include=["location"])
    # en_US mask is ##### -> 5 digits
    assert len(p.location.postal_code) == 5
    assert p.location.postal_code.isdigit()


def test_location_is_geographically_coherent() -> None:
    # city, region, timezone and coordinates must all come from one place, so a
    # city always maps to its real region/timezone and coords land in-locale.
    from persona_factory.data import load_locale

    places = {p["city"]: p for p in load_locale("en_GB", "data.json")["places"]}
    for seed in range(25):
        loc = PersonaFactory("en_GB", seed=seed).generate(include=["location"]).location
        place = places[loc.city]
        assert loc.region == place["region"]
        assert loc.timezone == place["timezone"]
        # jittered but still within ~6km of the city centre
        assert abs(loc.latitude - place["lat"]) <= 0.06
        assert abs(loc.longitude - place["lon"]) <= 0.06


def test_location_city_override_pulls_matching_region() -> None:
    p = PersonaFactory("en_GB", seed=1).generate(**{"location.city": "Bristol"})
    assert p.location.city == "Bristol"
    assert p.location.region == "South West England"  # not "Yorkshire"


def test_education_not_above_age() -> None:
    f = PersonaFactory("en_US")
    for seed in range(40):
        p = f.generate(seed=seed, age=18, include=["identity", "socioeconomic"])
        assert p.socioeconomic.education_level not in {"master", "doctorate", "professional"}


def test_education_override_survives_age_clamp() -> None:
    p = PersonaFactory("en_US", seed=1).generate(
        age=18, education_level="master", include=["identity", "socioeconomic"]
    )
    assert p.socioeconomic.education_level == "master"


def test_body_type_coheres_with_bmi() -> None:
    f = PersonaFactory("en_US")
    for seed in range(60):
        ph = f.generate(seed=seed, gender="male", include=["identity", "physical"]).physical
        bmi = ph.weight_kg / ((ph.height_cm / 100) ** 2)
        if bmi < 20:
            assert ph.body_type not in {"heavyset", "curvy"}
        if bmi > 32:
            assert ph.body_type != "slim"


def test_ip_uses_documentation_range() -> None:
    for seed in range(20):
        p = PersonaFactory("en_US", seed=seed).generate(include=["identity", "contact"])
        assert p.contact.ip_address.startswith(("192.0.2.", "198.51.100.", "203.0.113."))


def test_iban_marked_synthetic_with_invalid_checkdigits() -> None:
    p = PersonaFactory("en_US", seed=1).generate(include=["documents"])
    # check digits (chars 3-4) are "00", invalid in real IBANs (02-98)
    assert p.documents.iban[2:4] == "00"


def test_non_latin_handle_reflects_romanized_name() -> None:
    for locale in ["zh_CN", "ja_JP", "ar_SA", "hi_IN", "ru_RU"]:
        p = PersonaFactory(locale, seed=1).generate(include=["identity", "contact"])
        assert not p.contact.username.startswith("user"), locale


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


def test_unseeded_generate_randomizes() -> None:
    # No seed -> each call should draw fresh entropy. Regression: ``derive``
    # keys child streams off the parent seed, so a passthrough ``None`` seed
    # produced the *same* persona every time.
    f = PersonaFactory("en_US")
    names = {f.generate(include=["identity"]).identity.full_name for _ in range(8)}
    assert len(names) > 1


def test_unseeded_generate_records_concrete_seed() -> None:
    # The drawn seed lands in meta so a "random" persona stays reproducible.
    p = PersonaFactory("en_US").generate(include=["identity"])
    recorded = p.meta["seed"]
    assert recorded is not None
    again = PersonaFactory("en_US").generate(seed=recorded, include=["identity"])
    assert again.identity.full_name == p.identity.full_name


def test_narrative_bio_mentions_name() -> None:
    p = PersonaFactory("en_US", seed=1).generate(given_name="Ada", include=list(ALL_DOMAINS))
    assert "Ada" in p.narrative.bio
