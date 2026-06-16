"""Seeded random-number wrapper that guarantees reproducibility.

Every source of randomness in persona-factory MUST flow through an :class:`RNG`
instance. Generators never call the global :mod:`random` module directly, so a
given ``seed`` always produces byte-identical personas across processes and
platforms (CPython's Mersenne-Twister stream is stable).
"""

from __future__ import annotations

import hashlib
import random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def _coerce_seed(seed: int | str | bytes | None) -> int | None:
    """Turn an arbitrary seed into a stable integer (or ``None`` for entropy).

    ``random.Random`` already hashes str/bytes seeds, but it uses the salted
    builtin ``hash`` for some types; we route text through SHA-256 so the same
    string always yields the same stream regardless of ``PYTHONHASHSEED``.
    """
    if seed is None or isinstance(seed, int):
        return seed
    if isinstance(seed, str):
        seed = seed.encode("utf-8")
    digest = hashlib.sha256(seed).digest()
    return int.from_bytes(digest[:8], "big")


class RNG:
    """A thin, deterministic facade over :class:`random.Random`.

    Parameters
    ----------
    seed:
        An ``int``, ``str``, ``bytes`` or ``None``. Text seeds are hashed with
        SHA-256 so they are stable across interpreter restarts.
    """

    __slots__ = ("_random", "_seed")

    def __init__(self, seed: int | str | bytes | None = None) -> None:
        self._seed = seed
        self._random = random.Random(_coerce_seed(seed))

    @property
    def seed(self) -> int | str | bytes | None:
        return self._seed

    # -- sub-streams -----------------------------------------------------
    def derive(self, label: str) -> RNG:
        """Return an independent child RNG keyed by ``label``.

        Useful for giving each generator its own deterministic stream so that
        enabling/disabling one domain does not perturb the others.
        """
        material = f"{self._seed!r}:{label}"
        return RNG(material)

    # -- primitives ------------------------------------------------------
    def random(self) -> float:
        """Return a float in ``[0.0, 1.0)``."""
        return self._random.random()

    def randint(self, low: int, high: int) -> int:
        """Return an int in the inclusive range ``[low, high]``."""
        return self._random.randint(low, high)

    def uniform(self, low: float, high: float) -> float:
        return self._random.uniform(low, high)

    def gauss(self, mu: float, sigma: float) -> float:
        return self._random.gauss(mu, sigma)

    def choice(self, seq: Sequence[T]) -> T:
        if not seq:
            raise IndexError("cannot choose from an empty sequence")
        return self._random.choice(seq)

    def sample(self, population: Sequence[T], k: int) -> list[T]:
        return self._random.sample(list(population), k)

    def shuffle(self, seq: list[T]) -> None:
        self._random.shuffle(seq)

    def weighted_choice(
        self, choices: Sequence[T], weights: Sequence[float] | None = None
    ) -> T:
        """Pick one element, optionally weighted. Falls back to uniform."""
        if not choices:
            raise IndexError("cannot choose from an empty sequence")
        if weights is None:
            return self._random.choice(choices)
        return self._random.choices(choices, weights=list(weights), k=1)[0]

    def weighted_sample(
        self,
        choices: Sequence[T],
        weights: Sequence[float] | None = None,
        k: int = 1,
    ) -> list[T]:
        """Pick ``k`` distinct elements honoring weights (no replacement).

        Implemented with the Efraimidis-Spirakis algorithm so it stays
        deterministic and unbiased under the seeded stream.
        """
        items = list(choices)
        if k >= len(items):
            result = list(items)
            self.shuffle(result)
            return result
        if weights is None:
            return self.sample(items, k)
        keyed = []
        for item, weight in zip(items, weights, strict=False):
            w = max(float(weight), 1e-12)
            # key = u**(1/w); larger key -> selected
            key = self._random.random() ** (1.0 / w)
            keyed.append((key, item))
        keyed.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in keyed[:k]]

    def chance(self, probability: float) -> bool:
        """Return ``True`` with the given probability in ``[0, 1]``."""
        return self._random.random() < probability

    def bounded_gauss(
        self, mu: float, sigma: float, low: float, high: float
    ) -> float:
        """A Gaussian clamped to ``[low, high]`` (re-rolls a few times first)."""
        for _ in range(8):
            value = self._random.gauss(mu, sigma)
            if low <= value <= high:
                return value
        return min(max(self._random.gauss(mu, sigma), low), high)
