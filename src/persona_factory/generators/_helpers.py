"""Shared sampling helpers that honor per-attribute config overrides.

Generators call :func:`pick` / :func:`pick_number` instead of touching the RNG
directly for any attribute that should be user-overridable. These functions
consult the :class:`~persona_factory.config.AttributeSpec` for the attribute's
dotted path and apply ``fixed`` / ``choices`` / range constraints transparently.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypeVar

from persona_factory.config import PersonaConfig
from persona_factory.rng import RNG

T = TypeVar("T")


def pick(
    rng: RNG,
    config: PersonaConfig,
    path: str,
    choices: Sequence[T],
    weights: Sequence[float] | None = None,
) -> T:
    """Choose one value for ``path``, applying any config override.

    Precedence: ``fixed`` > config ``choices``/``weights`` > generator defaults.
    """
    spec = config.spec_for(path)
    if spec is not None:
        if spec.fixed is not None:
            return spec.fixed  # type: ignore[no-any-return]
        if spec.choices is not None:
            return rng.weighted_choice(spec.choices, spec.weights)  # type: ignore[no-any-return]
    return rng.weighted_choice(choices, weights)


def pick_sample(
    rng: RNG,
    config: PersonaConfig,
    path: str,
    choices: Sequence[T],
    k: int,
    weights: Sequence[float] | None = None,
) -> list[T]:
    """Choose up to ``k`` distinct values for ``path``, honoring a config override."""
    spec = config.spec_for(path)
    if spec is not None:
        if spec.fixed is not None:
            return list(spec.fixed)
        if spec.choices is not None:
            return rng.weighted_sample(spec.choices, spec.weights, k=k)
    return rng.weighted_sample(choices, weights, k=k)


def pick_number(
    rng: RNG,
    config: PersonaConfig,
    path: str,
    low: float,
    high: float,
    *,
    integer: bool = False,
    mu: float | None = None,
    sigma: float | None = None,
) -> float:
    """Sample a number in ``[low, high]``, applying config ``fixed``/range overrides.

    When ``mu``/``sigma`` are given the value is drawn from a clamped Gaussian,
    otherwise uniform.
    """
    spec = config.spec_for(path)
    if spec is not None:
        if spec.fixed is not None:
            return float(spec.fixed)
        if spec.min_value is not None:
            low = max(low, spec.min_value)
        if spec.max_value is not None:
            high = min(high, spec.max_value)
    if low > high:
        low, high = high, low
    if mu is not None and sigma is not None:
        value = rng.bounded_gauss(mu, sigma, low, high)
    else:
        value = rng.uniform(low, high)
    if integer:
        return float(round(value))
    return value


def is_fixed(config: PersonaConfig, path: str) -> Any | None:
    """Return the fixed value for ``path`` if one is configured, else ``None``."""
    spec = config.spec_for(path)
    return spec.fixed if spec is not None else None
