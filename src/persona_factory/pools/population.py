"""Generate and manipulate pools of personas.

:func:`generate_pool` produces ``n`` personas with per-persona reproducible
seeds derived from the pool seed (so the whole pool is reproducible, and
individual personas can be regenerated independently).

``distributions`` lets a caller pin the *aggregate* shape of the pool: a mapping
from an override keyword (e.g. ``"gender"``, ``"locale"``) to a
``value -> proportion`` mapping. The pool deterministically allocates counts to
each value (largest-remainder rounding) and assigns them across the personas, so
a 1000-persona pool asked for 50% female really contains ~500 females rather
than relying on sampling noise.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from persona_factory.models.persona import Persona
from persona_factory.rng import RNG

if TYPE_CHECKING:
    from persona_factory.factory import PersonaFactory


class PersonaPool:
    """A reproducible collection of :class:`Persona` objects."""

    def __init__(self, personas: list[Persona], meta: dict[str, Any] | None = None):
        self._personas = personas
        self.meta = meta or {}

    # -- container protocol ---------------------------------------------
    def __len__(self) -> int:
        return len(self._personas)

    def __iter__(self) -> Iterator[Persona]:
        return iter(self._personas)

    def __getitem__(self, index: int) -> Persona:
        return self._personas[index]

    @property
    def personas(self) -> list[Persona]:
        return self._personas

    # -- querying --------------------------------------------------------
    def filter(self, predicate: Any) -> PersonaPool:
        """Return a new pool keeping personas for which ``predicate`` is truthy."""
        return PersonaPool([p for p in self._personas if predicate(p)], self.meta)

    def counts(self, attribute: str) -> dict[Any, int]:
        """Tally a dotted attribute path across the pool (e.g. ``"identity.gender"``)."""
        tally: dict[Any, int] = {}
        for persona in self._personas:
            value = _resolve_path(persona, attribute)
            tally[value] = tally.get(value, 0) + 1
        return dict(sorted(tally.items(), key=lambda kv: (-kv[1], str(kv[0]))))

    def unique_count(self, attribute: str) -> int:
        """Number of distinct values for an attribute path."""
        return len({_resolve_path(p, attribute) for p in self._personas})

    # -- serialization ---------------------------------------------------
    def to_list(self, *, exclude_none: bool = True) -> list[dict[str, Any]]:
        return [p.to_dict(exclude_none=exclude_none) for p in self._personas]

    def to_jsonl(self, *, exclude_none: bool = True) -> str:
        """Render the pool as newline-delimited JSON (one persona per line)."""
        return "\n".join(
            json.dumps(p.to_dict(exclude_none=exclude_none), ensure_ascii=False)
            for p in self._personas
        )

    def to_dataframe(self) -> Any:
        """Return a flat :class:`polars.DataFrame` (requires the ``polars`` extra).

        Each persona becomes one row; nested domains are flattened into
        dotted columns (e.g. ``identity.given_name``, ``physical.height_cm``).
        List-valued attributes are kept as list columns.
        """
        try:
            import polars as pl
        except ImportError as exc:  # pragma: no cover - optional dep
            raise ImportError(
                "PersonaPool.to_dataframe requires the 'polars' extra: "
                "pip install 'persona-factory[polars]'"
            ) from exc
        rows = [_flatten_dict(p.to_dict()) for p in self._personas]
        return pl.DataFrame(rows)


def _flatten_dict(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten one level of nested domain dicts into dotted keys.

    Nested objects (sub-models) become ``parent.child`` columns; lists and
    scalars are left as-is so polars can infer list/scalar column types.
    """
    flat: dict[str, Any] = {}
    for key, value in data.items():
        dotted = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(_flatten_dict(value, prefix=f"{dotted}."))
        else:
            flat[dotted] = value
    return flat


def _resolve_path(persona: Persona, path: str) -> Any:
    obj: Any = persona
    for part in path.split("."):
        if obj is None:
            return None
        obj = getattr(obj, part, None)
    return obj


def _allocate_counts(n: int, proportions: dict[Any, float]) -> dict[Any, int]:
    """Split ``n`` items across keys by proportion (largest-remainder rounding)."""
    total = sum(proportions.values())
    if total <= 0:
        return {}
    raw = {k: n * (v / total) for k, v in proportions.items()}
    counts = {k: int(v) for k, v in raw.items()}
    remainder = n - sum(counts.values())
    # distribute the remaining slots to the largest fractional parts
    fractions = sorted(raw.items(), key=lambda kv: kv[1] - int(kv[1]), reverse=True)
    for i in range(remainder):
        counts[fractions[i % len(fractions)][0]] += 1
    return counts


def _factory_for_locale(
    base: PersonaFactory,
    locale: str | None,
    cache: dict[str, PersonaFactory],
) -> PersonaFactory:
    """Return a factory bound to ``locale`` (cached), reusing ``base``'s config."""
    if locale is None or locale == base.config.locale:
        return base
    if locale not in cache:
        from persona_factory.factory import PersonaFactory

        new_config = base.config.model_copy(update={"locale": locale})
        cache[locale] = PersonaFactory(config=new_config)
    return cache[locale]


def generate_pool(
    factory: PersonaFactory,
    n: int,
    distributions: dict[str, dict[Any, float]] | None = None,
    seed: int | str | None = None,
) -> PersonaPool:
    """Generate a :class:`PersonaPool` of ``n`` personas.

    Parameters
    ----------
    factory:
        The :class:`PersonaFactory` to generate with.
    n:
        Number of personas.
    distributions:
        Optional aggregate constraints, e.g.
        ``{"gender": {"female": 0.5, "male": 0.5}}``. Counts are allocated
        deterministically so the pool matches the requested shape.
    seed:
        Pool seed; per-persona seeds derive from it. Defaults to the factory's
        configured seed.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    pool_seed = seed if seed is not None else factory.config.seed
    rng = RNG(pool_seed).derive("pool")

    distributions = dict(distributions or {})
    # If the config declares locale_weights and the caller didn't override
    # locale, treat the weights as a locale distribution for the pool.
    if "locale" not in distributions and factory.config.locale_weights:
        distributions["locale"] = dict(factory.config.locale_weights)

    # Build a per-persona override plan honoring the requested distributions.
    plan: list[dict[str, Any]] = [{} for _ in range(n)]
    for keyword, proportions in distributions.items():
        counts = _allocate_counts(n, proportions)
        assignments: list[Any] = []
        for value, count in counts.items():
            assignments.extend([value] * count)
        # pad/trim to exactly n (rounding safety)
        while len(assignments) < n:
            assignments.append(assignments[-1] if assignments else None)
        assignments = assignments[:n]
        rng.shuffle(assignments)
        for i, value in enumerate(assignments):
            if value is not None:
                plan[i][keyword] = value

    personas: list[Persona] = []
    factory_cache: dict[str, PersonaFactory] = {factory.config.locale: factory}
    for i in range(n):
        persona_seed = f"{pool_seed}:persona:{i}"
        overrides = dict(plan[i])
        # locale changes which factory/locale-data we generate from
        locale = overrides.pop("locale", None)
        gen_factory = _factory_for_locale(factory, locale, factory_cache)
        personas.append(gen_factory.generate(seed=persona_seed, **overrides))

    meta = {
        "size": n,
        "seed": pool_seed,
        "distributions": distributions,
    }
    return PersonaPool(personas, meta)
