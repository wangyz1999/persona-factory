"""Integrity tests for bundled data files."""

from __future__ import annotations

import pytest

from persona_factory.data import available_locales, load_locale

REQUIRED_KEYS = {
    "country",
    "country_code",
    "language",
    "script",
    "currency",
    "given_names",
    "surnames",
    "cities",
    "regions",
    "email_domains",
}


def test_locales_present() -> None:
    locs = available_locales()
    assert "en_US" in locs
    assert len(locs) >= 10


@pytest.mark.parametrize("locale", list(available_locales()))
def test_locale_has_required_keys(locale: str) -> None:
    data = load_locale(locale, "data.json")
    missing = REQUIRED_KEYS - data.keys()
    assert not missing, f"{locale} missing {missing}"


@pytest.mark.parametrize("locale", list(available_locales()))
def test_locale_name_pools_nonempty(locale: str) -> None:
    data = load_locale(locale, "data.json")
    assert data["given_names"].get("male")
    assert data["given_names"].get("female")
    assert data["surnames"]
