"""Tests for population pool generation."""

from __future__ import annotations

import json

import pytest

from persona_factory.config import ALL_DOMAINS
from persona_factory.factory import PersonaFactory
from persona_factory.pools.population import _allocate_counts


def test_pool_size() -> None:
    pool = PersonaFactory("en_US", seed=1).generate_pool(50)
    assert len(pool) == 50
    assert len(list(pool)) == 50


def test_pool_reproducible() -> None:
    a = PersonaFactory("en_US", seed=1).generate_pool(20)
    b = PersonaFactory("en_US", seed=1).generate_pool(20)
    assert a.to_jsonl() == b.to_jsonl()


def test_distribution_allocation_exact() -> None:
    pool = PersonaFactory("en_US", seed=2).generate_pool(
        100, distributions={"gender": {"female": 0.5, "male": 0.5}}
    )
    counts = pool.counts("identity.gender")
    assert counts.get("female") == 50
    assert counts.get("male") == 50


def test_allocate_counts_sums_to_n() -> None:
    counts = _allocate_counts(1000, {"a": 0.333, "b": 0.333, "c": 0.334})
    assert sum(counts.values()) == 1000


def test_identity_uniqueness_in_pool() -> None:
    pool = PersonaFactory("en_US", seed=3).generate_pool(
        200, distributions={"gender": {"female": 0.5, "male": 0.5}}
    )
    # bios are highly distinctive; expect all unique
    assert pool.unique_count("narrative.bio") == len(pool)


def test_email_uniqueness_when_contact_enabled() -> None:
    factory = PersonaFactory("en_US", seed=3)
    factory.config = factory.config.model_copy(update={"include": list(ALL_DOMAINS)})
    pool = factory.generate_pool(200)
    assert pool.unique_count("contact.email") == len(pool)


def test_jsonl_is_valid_json_per_line() -> None:
    pool = PersonaFactory("en_US", seed=4).generate_pool(10)
    lines = pool.to_jsonl().splitlines()
    assert len(lines) == 10
    for line in lines:
        json.loads(line)  # must not raise


def test_pool_filter() -> None:
    pool = PersonaFactory("en_US", seed=5).generate_pool(
        100, distributions={"gender": {"female": 0.5, "male": 0.5}}
    )
    females = pool.filter(lambda p: p.identity.gender == "female")
    assert all(p.identity.gender == "female" for p in females)
    assert len(females) == 50


def test_negative_size_rejected() -> None:
    with pytest.raises(ValueError):
        PersonaFactory("en_US", seed=1).generate_pool(-1)


def test_to_dataframe_flattens_to_dotted_columns() -> None:
    pl = pytest.importorskip("polars")
    pool = PersonaFactory("en_US", seed=1).generate_pool(5)
    df = pool.to_dataframe()
    assert isinstance(df, pl.DataFrame)
    assert df.height == 5
    assert "identity.given_name" in df.columns
    assert "identity.gender" in df.columns


def test_locale_weights_drive_pool_locales() -> None:
    from persona_factory.config import PersonaConfig

    cfg = PersonaConfig(
        locale="en_US", locale_weights={"en_US": 0.5, "ja_JP": 0.5}, seed=1
    )
    pool = PersonaFactory(config=cfg).generate_pool(100)
    locales = pool.counts("identity.locale")
    assert locales.get("en_US") == 50
    assert locales.get("ja_JP") == 50
