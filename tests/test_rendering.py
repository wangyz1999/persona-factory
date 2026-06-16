"""Tests for rendering personas to prompts, cards, and serialized forms."""

from __future__ import annotations

import json

import pytest

from persona_factory.config import ALL_DOMAINS
from persona_factory.factory import PersonaFactory


def _persona():  # type: ignore[no-untyped-def]
    return PersonaFactory("en_US", seed=42).generate(include=list(ALL_DOMAINS))


def test_system_prompt_roleplay_is_second_person() -> None:
    p = _persona()
    prompt = p.to_system_prompt()
    assert prompt.startswith(f"You are {p.display_name}")
    assert "Stay in character" in prompt


def test_system_prompt_profile_style() -> None:
    p = _persona()
    prompt = p.to_system_prompt(style="profile")
    assert prompt.startswith("# Persona Profile")


def test_system_prompt_rejects_bad_style() -> None:
    with pytest.raises(ValueError):
        _persona().to_system_prompt(style="nonsense")


def test_system_prompt_only_includes_present_domains() -> None:
    p = PersonaFactory("en_US", seed=1).generate(include=["identity"])
    prompt = p.to_system_prompt()
    # no work/personality lines when those domains are off
    assert "Work & education" not in prompt
    assert "Personality" not in prompt


def test_markdown_card_has_headings() -> None:
    p = _persona()
    card = p.to_markdown_card()
    assert card.startswith(f"# {p.display_name}")
    assert "## Identity" in card
    assert "## Personality" in card


def test_card_skips_empty_sections() -> None:
    p = PersonaFactory("en_US", seed=1).generate(include=["identity"])
    card = p.to_markdown_card()
    assert "## Physical" not in card


def test_to_json_roundtrips() -> None:
    p = _persona()
    data = json.loads(p.to_json())
    assert data["identity"]["given_name"]


def test_to_dict_excludes_none_by_default() -> None:
    p = PersonaFactory("en_US", seed=1).generate(include=["identity"])
    d = p.to_dict()
    # middle_name often None -> excluded
    assert "physical" not in d


def test_card_renders_ocean_compactly() -> None:
    p = _persona()
    card = p.to_markdown_card()
    assert "OCEAN" in card
