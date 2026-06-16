"""Tests for the seeded RNG wrapper."""

from __future__ import annotations

from persona_factory.rng import RNG


def test_int_seed_is_reproducible() -> None:
    a = [RNG(42).randint(0, 1_000_000) for _ in range(1)]
    b = [RNG(42).randint(0, 1_000_000) for _ in range(1)]
    assert a == b


def test_string_seed_stable_across_instances() -> None:
    r1 = RNG("hello-world")
    r2 = RNG("hello-world")
    assert [r1.random() for _ in range(5)] == [r2.random() for _ in range(5)]


def test_different_seeds_differ() -> None:
    assert RNG(1).randint(0, 10**9) != RNG(2).randint(0, 10**9)


def test_derive_is_deterministic_and_independent() -> None:
    parent = RNG(99)
    a = parent.derive("identity").randint(0, 1000)
    b = RNG(99).derive("identity").randint(0, 1000)
    assert a == b


def test_weighted_choice_respects_zero_weights() -> None:
    for _ in range(20):
        assert RNG(_).weighted_choice(["a", "b", "c"], [1, 0, 0]) == "a"


def test_weighted_sample_no_replacement() -> None:
    out = RNG(3).weighted_sample(["a", "b", "c", "d"], [10, 10, 1, 1], k=2)
    assert len(out) == 2
    assert len(set(out)) == 2


def test_bounded_gauss_stays_in_range() -> None:
    rng = RNG(5)
    for _ in range(100):
        v = rng.bounded_gauss(50, 30, 0, 100)
        assert 0 <= v <= 100


def test_chance_extremes() -> None:
    rng = RNG(7)
    assert all(rng.chance(1.0) for _ in range(10))
    assert not any(rng.chance(0.0) for _ in range(10))
