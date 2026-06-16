"""persona-factory: generate richly-attributed, coherent fake personas.

This module is the public API surface. Import the high-level entrypoints from
here; everything else is considered internal and may change between releases.

Example
-------
>>> from persona_factory import PersonaFactory
>>> factory = PersonaFactory(locale="en_US", seed=42)
>>> person = factory.generate(gender="female", age_range=(25, 35), mbti="INTJ")
>>> print(person.to_system_prompt())  # doctest: +SKIP
"""

from __future__ import annotations

from persona_factory import presets
from persona_factory.config import AttributeSpec, PersonaConfig
from persona_factory.data import available_locales
from persona_factory.exceptions import (
    ConfigError,
    DataError,
    EnrichmentError,
    InvalidOverrideError,
    PersonaFactoryError,
    UnknownLocaleError,
    UnknownPresetError,
)
from persona_factory.factory import PersonaFactory
from persona_factory.models.persona import Persona
from persona_factory.pools.population import PersonaPool
from persona_factory.rng import RNG

__version__ = "0.1.1"

__all__ = [
    "RNG",
    "AttributeSpec",
    "ConfigError",
    "DataError",
    "EnrichmentError",
    "InvalidOverrideError",
    "Persona",
    "PersonaConfig",
    "PersonaFactory",
    "PersonaFactoryError",
    "PersonaPool",
    "UnknownLocaleError",
    "UnknownPresetError",
    "__version__",
    "available_locales",
    "presets",
]
