"""Tests for the optional Claude enrichment module (mocked — no live API)."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from persona_factory.enrichment.claude import _build_prompt, enrich
from persona_factory.exceptions import EnrichmentError
from persona_factory.factory import PersonaFactory


class _FakeBlock:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _FakeMessages:
    def __init__(self, payload: dict, capture: dict) -> None:
        self._payload = payload
        self._capture = capture

    def create(self, **kwargs):  # type: ignore[no-untyped-def]
        self._capture.update(kwargs)
        return SimpleNamespace(content=[_FakeBlock(json.dumps(self._payload))])


class _FakeClient:
    def __init__(self, payload: dict) -> None:
        self.captured: dict = {}
        self.messages = _FakeMessages(payload, self.captured)


def _persona():  # type: ignore[no-untyped-def]
    return PersonaFactory("en_US", seed=1).generate()


def test_enrich_writes_backstory_and_bio() -> None:
    payload = {
        "bio": "A vivid third-person bio.",
        "backstory": "I grew up by the sea...",
        "sample_dialogue": ["Hey there!", "Sure, why not."],
    }
    client = _FakeClient(payload)
    p = enrich(_persona(), backstory=True, sample_dialogue=True, client=client)
    assert p.narrative.bio == "A vivid third-person bio."
    assert p.narrative.backstory.startswith("I grew up")
    assert p.narrative.sample_dialogue == ["Hey there!", "Sure, why not."]


def test_enrich_skips_dialogue_when_not_requested() -> None:
    payload = {"bio": "b", "backstory": "s", "sample_dialogue": ["x"]}
    client = _FakeClient(payload)
    p = enrich(_persona(), sample_dialogue=False, client=client)
    assert p.narrative.sample_dialogue == []


def test_enrich_noop_when_nothing_requested() -> None:
    client = _FakeClient({})
    p = _persona()
    original = p.narrative.bio
    out = enrich(p, backstory=False, sample_dialogue=False, client=client)
    assert out.narrative.bio == original
    assert client.captured == {}  # no API call made


def test_enrich_uses_default_model() -> None:
    client = _FakeClient({"bio": "b", "backstory": "s", "sample_dialogue": []})
    enrich(_persona(), client=client)
    assert client.captured["model"] == "claude-sonnet-4-6"


def test_enrich_passes_structured_output_schema() -> None:
    client = _FakeClient({"bio": "b", "backstory": "s", "sample_dialogue": []})
    enrich(_persona(), client=client)
    fmt = client.captured["output_config"]["format"]
    assert fmt["type"] == "json_schema"
    assert "bio" in fmt["schema"]["properties"]


def test_enrich_raises_on_invalid_json() -> None:
    class BadMessages:
        def create(self, **kwargs):  # type: ignore[no-untyped-def]
            return SimpleNamespace(content=[_FakeBlock("not json")])

    client = SimpleNamespace(messages=BadMessages())
    with pytest.raises(EnrichmentError):
        enrich(_persona(), client=client)


def test_build_prompt_includes_persona_facts() -> None:
    p = PersonaFactory("en_US", seed=1).generate(given_name="Ada")
    prompt = _build_prompt(p, sample_dialogue=True)
    assert "Ada" in prompt
    assert "sample_dialogue" in prompt


def test_missing_extra_raises_friendly_error(monkeypatch) -> None:
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name == "anthropic":
            raise ImportError("no anthropic")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(EnrichmentError, match="enrichment"):
        enrich(_persona(), client=None)
