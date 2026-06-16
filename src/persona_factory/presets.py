"""Bundled :class:`~persona_factory.config.PersonaConfig` presets.

Presets are ready-made configs for common scenarios. Fetch one by name with
:func:`get` (or list them with :func:`names`) and pass it to
:class:`~persona_factory.factory.PersonaFactory`::

    from persona_factory import PersonaFactory, presets
    factory = PersonaFactory(config=presets.get("gen_z_global"))
"""

from __future__ import annotations

from persona_factory.config import AttributeSpec, PersonaConfig
from persona_factory.exceptions import UnknownPresetError

# Each preset is a zero-arg builder so callers always get a fresh, mutable copy.
_PRESETS = {
    "realistic_us_adult": lambda: PersonaConfig(
        locale="en_US",
        attributes={"identity.age": AttributeSpec(min_value=18, max_value=75)},
    ),
    "gen_z_global": lambda: PersonaConfig(
        locale="en_US",
        locale_weights={
            "en_US": 0.3,
            "en_GB": 0.15,
            "ja_JP": 0.12,
            "pt_BR": 0.12,
            "es_ES": 0.1,
            "fr_FR": 0.1,
            "hi_IN": 0.11,
        },
        attributes={
            "identity.age": AttributeSpec(min_value=13, max_value=28),
            "lifestyle.tech_savviness": AttributeSpec(
                choices=["proficient", "expert"], weights=[0.5, 0.5]
            ),
            "communication.emoji_usage": AttributeSpec(
                choices=["moderate", "frequent", "heavy"], weights=[0.3, 0.4, 0.3]
            ),
        },
    ),
    "enterprise_personas": lambda: PersonaConfig(
        locale="en_US",
        include=[
            "identity",
            "contact",
            "location",
            "socioeconomic",
            "personality",
            "communication",
        ],
        attributes={
            "identity.age": AttributeSpec(min_value=22, max_value=65),
            "socioeconomic.employment_status": AttributeSpec(fixed="employed_full_time"),
            "communication.formality": AttributeSpec(
                choices=["formal", "neutral"], weights=[0.5, 0.5]
            ),
        },
    ),
    "minimal_identity": lambda: PersonaConfig(
        locale="en_US",
        include=["identity"],
    ),
    "full_dossier": lambda: PersonaConfig(
        locale="en_US",
        include=[
            "identity",
            "physical",
            "contact",
            "location",
            "socioeconomic",
            "personality",
            "values",
            "beliefs",
            "lifestyle",
            "social",
            "communication",
            "narrative",
            "documents",
        ],
    ),
    "elderly_retiree": lambda: PersonaConfig(
        locale="en_US",
        attributes={
            "identity.age": AttributeSpec(min_value=65, max_value=90),
            "socioeconomic.employment_status": AttributeSpec(fixed="retired"),
        },
    ),
}


def names() -> list[str]:
    """Return the sorted list of available preset names."""
    return sorted(_PRESETS)


def get(name: str) -> PersonaConfig:
    """Return a fresh :class:`PersonaConfig` for ``name``.

    Raises :class:`~persona_factory.exceptions.UnknownPresetError` if unknown.
    """
    builder = _PRESETS.get(name)
    if builder is None:
        raise UnknownPresetError(name, names())
    return builder()
