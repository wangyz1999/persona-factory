"""persona-factory: generate richly-attributed, coherent fake personas.

This module is the public API surface. Import the high-level entrypoints from
here; everything else is considered internal and may change between releases.
"""

from __future__ import annotations

from persona_factory.exceptions import (
    ConfigError,
    DataError,
    EnrichmentError,
    InvalidOverrideError,
    PersonaFactoryError,
    UnknownLocaleError,
    UnknownPresetError,
)
from persona_factory.rng import RNG

__version__ = "0.1.0"

__all__ = [
    "RNG",
    "ConfigError",
    "DataError",
    "EnrichmentError",
    "InvalidOverrideError",
    "PersonaFactoryError",
    "UnknownLocaleError",
    "UnknownPresetError",
    "__version__",
]
