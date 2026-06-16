"""Generate a 1,000-persona pool matching target distributions.

Run with:  uv run python examples/pool.py
"""

from __future__ import annotations

from persona_factory import PersonaFactory


def main() -> None:
    factory = PersonaFactory(locale="en_US", seed=2025)
    pool = factory.generate_pool(
        1000,
        distributions={
            "gender": {"female": 0.50, "male": 0.48, "non_binary": 0.02},
        },
    )

    print(f"Generated {len(pool)} personas.\n")

    print("Gender distribution:")
    for value, count in pool.counts("identity.gender").items():
        print(f"  {value:<12} {count:>4}  ({count / len(pool):.0%})")

    print(f"\nUnique bios: {pool.unique_count('narrative.bio')} / {len(pool)}")

    # Write to JSONL for downstream use.
    out = "people.jsonl"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(pool.to_jsonl())
    print(f"\nWrote {len(pool)} personas to {out}")

    print("\nFirst persona:")
    print(" ", pool[0].display_name, "—", pool[0].socioeconomic.occupation)


if __name__ == "__main__":
    main()
