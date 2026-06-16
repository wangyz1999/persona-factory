"""Generator protocol and registry.

Each attribute *domain* (identity, physical, …) is produced by a
:class:`Generator`. The :class:`PersonaFactory` runs the enabled generators in
dependency order, passing each one the partial :class:`Persona` built so far so
later generators can read earlier results (e.g. communication style reading
personality).

Generators must be **pure with respect to their RNG**: all randomness comes from
the supplied :class:`~persona_factory.rng.RNG`, never the global ``random``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG


class Generator(ABC):
    """Base class for all domain generators.

    Subclasses set :attr:`domain` (the ``Persona`` field they populate) and
    :attr:`depends_on` (domains that must run first), then implement
    :meth:`generate` to mutate ``persona`` in place.
    """

    #: Name of the ``Persona`` attribute this generator fills (e.g. ``"identity"``).
    domain: str = ""
    #: Domains that must be generated before this one.
    depends_on: tuple[str, ...] = ()

    @abstractmethod
    def generate(
        self,
        rng: RNG,
        config: PersonaConfig,
        persona: Persona,
        locale_data: dict,
    ) -> None:
        """Populate ``persona.<domain>`` in place using ``rng`` and ``config``."""
        raise NotImplementedError


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
_REGISTRY: dict[str, Generator] = {}


def register(generator: Generator) -> Generator:
    """Register a generator instance under its ``domain`` key."""
    if not generator.domain:
        raise ValueError(f"{generator!r} has no domain set")
    _REGISTRY[generator.domain] = generator
    return generator


def get_registry() -> dict[str, Generator]:
    """Return the live registry (domain -> generator)."""
    return _REGISTRY


def ordered_domains(enabled: list[str]) -> list[str]:
    """Topologically sort ``enabled`` domains by their ``depends_on`` edges.

    Raises ``ValueError`` on an unknown domain or a dependency cycle.
    """
    enabled_set = set(enabled)
    result: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(domain: str) -> None:
        if domain in visited:
            return
        if domain in visiting:
            raise ValueError(f"dependency cycle detected at domain {domain!r}")
        if domain not in _REGISTRY:
            raise ValueError(f"no generator registered for domain {domain!r}")
        visiting.add(domain)
        for dep in _REGISTRY[domain].depends_on:
            if dep in enabled_set:
                visit(dep)
        visiting.discard(domain)
        visited.add(domain)
        result.append(domain)

    for domain in enabled:
        visit(domain)
    return result
