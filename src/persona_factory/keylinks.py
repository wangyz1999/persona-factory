"""Cross-domain key-link resolvers.

These enforce the small, fixed set of *inter-domain* coherence rules. They run
after all generators, so every domain is present (or ``None`` if disabled).
Each resolver is defensive: it does nothing if the domains it needs are absent.

Intra-domain links (name<->gender, age<->generation) live in the owning
generator, not here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from persona_factory.models.enums import (
    EmploymentStatus,
    IncomeBand,
    Seniority,
)

if TYPE_CHECKING:
    from persona_factory.config import PersonaConfig
    from persona_factory.models.persona import Persona
    from persona_factory.rng import RNG

# Occupation-category keywords -> plausible income-band ceiling/floor. Used only
# as a *sanity clamp*, not to overwrite an explicitly configured value.
_LOW_INCOME_HINTS = ("student", "intern", "unemployed", "retired", "homemaker")
_HIGH_INCOME_OCCUPATIONS = (
    "surgeon",
    "physician",
    "lawyer",
    "executive",
    "ceo",
    "pilot",
    "investment",
    "dentist",
)

_INCOME_ORDER = [
    IncomeBand.VERY_LOW,
    IncomeBand.LOW,
    IncomeBand.LOWER_MIDDLE,
    IncomeBand.MIDDLE,
    IncomeBand.UPPER_MIDDLE,
    IncomeBand.HIGH,
    IncomeBand.VERY_HIGH,
]


def _is_configured(config: PersonaConfig, path: str) -> bool:
    spec = config.spec_for(path)
    return spec is not None and spec.fixed is not None


def apply_cross_domain_links(
    persona: Persona,
    rng: RNG,
    config: PersonaConfig,
    locale_data: dict[str, Any],
) -> None:
    """Apply every cross-domain resolver in a fixed, deterministic order."""
    _link_currency(persona, locale_data)
    _link_employment_to_age(persona, config)
    _link_occupation_to_income(persona, config)
    _link_age_to_relationships(persona, config, rng)


def _link_currency(persona: Persona, locale_data: dict[str, Any]) -> None:
    """A persona's income currency follows their locale."""
    if persona.socioeconomic and not persona.socioeconomic.currency:
        persona.socioeconomic.currency = locale_data.get("currency")


def _link_employment_to_age(persona: Persona, config: PersonaConfig) -> None:
    """Very young/old personas get student/retired status unless configured."""
    socio = persona.socioeconomic
    age = persona.identity.age
    if socio is None or age is None:
        return
    if _is_configured(config, "socioeconomic.employment_status"):
        return
    if age >= 67:
        socio.employment_status = EmploymentStatus.RETIRED
    elif age <= 21:
        socio.employment_status = EmploymentStatus.STUDENT


def _link_occupation_to_income(persona: Persona, config: PersonaConfig) -> None:
    """Clamp income band into a plausible range for the occupation/status."""
    socio = persona.socioeconomic
    if socio is None or _is_configured(config, "socioeconomic.income_band"):
        return

    occ = (socio.occupation or "").lower()
    status = socio.employment_status

    # Non-earning statuses pull income to the low end.
    if status in {EmploymentStatus.STUDENT, EmploymentStatus.UNEMPLOYED} or any(
        h in occ for h in _LOW_INCOME_HINTS
    ):
        if socio.income_band is None or _band_index(socio.income_band) > _band_index(
            IncomeBand.LOWER_MIDDLE
        ):
            socio.income_band = IncomeBand.LOW
        return

    # High-earning professions raise the floor.
    if any(h in occ for h in _HIGH_INCOME_OCCUPATIONS) or socio.seniority in {
        Seniority.DIRECTOR,
        Seniority.EXECUTIVE,
    }:
        if socio.income_band is None or _band_index(socio.income_band) < _band_index(
            IncomeBand.UPPER_MIDDLE
        ):
            socio.income_band = IncomeBand.HIGH


def _link_age_to_relationships(persona: Persona, config: PersonaConfig, rng: RNG) -> None:
    """Minors and very young adults should not be married/have many children."""
    social = persona.social
    age = persona.identity.age
    if social is None or age is None:
        return
    if age < 18:
        from persona_factory.models.enums import MaritalStatus

        if not _is_configured(config, "social.marital_status"):
            social.marital_status = MaritalStatus.SINGLE
        if social.children:
            social.children = 0


def _band_index(band: IncomeBand) -> int:
    try:
        return _INCOME_ORDER.index(IncomeBand(band))
    except ValueError:  # pragma: no cover - defensive
        return _INCOME_ORDER.index(IncomeBand.MIDDLE)
