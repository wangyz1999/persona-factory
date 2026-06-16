"""Tests for PersonaConfig and bundled presets."""

from __future__ import annotations

import json

import pytest

from persona_factory import presets
from persona_factory.config import AttributeSpec, PersonaConfig
from persona_factory.exceptions import ConfigError, UnknownPresetError
from persona_factory.factory import PersonaFactory


def test_default_domains_exclude_documents() -> None:
    cfg = PersonaConfig()
    assert "documents" not in cfg.enabled_domains()
    assert "identity" in cfg.enabled_domains()


def test_include_overrides_defaults() -> None:
    cfg = PersonaConfig(include=["identity", "documents"])
    assert cfg.enabled_domains() == ["identity", "documents"]


def test_exclude_removes_domain() -> None:
    cfg = PersonaConfig(exclude=["narrative"])
    assert "narrative" not in cfg.enabled_domains()


def test_unknown_domain_rejected() -> None:
    with pytest.raises(ConfigError):
        PersonaConfig(include=["not_a_domain"])


def test_attribute_spec_weight_length_validated() -> None:
    with pytest.raises(ValueError):
        AttributeSpec(choices=["a", "b"], weights=[1.0])


def test_attribute_spec_range_validated() -> None:
    with pytest.raises(ValueError):
        AttributeSpec(min_value=10, max_value=5)


def test_config_from_dict_roundtrip() -> None:
    data = {
        "locale": "fr_FR",
        "seed": 7,
        "attributes": {"identity.age": {"min_value": 30, "max_value": 40}},
    }
    cfg = PersonaConfig.from_dict(data)
    assert cfg.locale == "fr_FR"
    assert cfg.spec_for("identity.age").min_value == 30


def test_config_from_json_file(tmp_path) -> None:
    path = tmp_path / "cfg.json"
    path.write_text(json.dumps({"locale": "de_DE", "seed": 1}))
    cfg = PersonaConfig.from_file(path)
    assert cfg.locale == "de_DE"


def test_all_presets_loadable() -> None:
    for name in presets.names():
        cfg = presets.get(name)
        assert isinstance(cfg, PersonaConfig)


def test_unknown_preset_raises() -> None:
    with pytest.raises(UnknownPresetError):
        presets.get("does_not_exist")


def test_preset_age_constraint_applied() -> None:
    factory = PersonaFactory(config=presets.get("elderly_retiree"))
    for _ in range(20):
        p = factory.generate()
        assert p.identity.age >= 65
        assert p.socioeconomic.employment_status == "retired"


def test_minimal_identity_preset_only_identity() -> None:
    factory = PersonaFactory(config=presets.get("minimal_identity"))
    p = factory.generate()
    assert p.identity.given_name
    assert p.physical is None
    assert p.socioeconomic is None
