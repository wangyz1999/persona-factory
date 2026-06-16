"""Domain generators.

Importing this package registers every built-in generator as a side effect, so
the factory only needs ``import persona_factory.generators``.
"""

from __future__ import annotations

from persona_factory.generators import (  # noqa: F401
    beliefs,
    communication,
    contact,
    documents,
    identity,
    lifestyle,
    location,
    narrative,
    personality,
    physical,
    social,
    socioeconomic,
    values,
)
from persona_factory.generators.base import (
    Generator,
    get_registry,
    ordered_domains,
    register,
)

__all__ = [
    "Generator",
    "get_registry",
    "ordered_domains",
    "register",
]
