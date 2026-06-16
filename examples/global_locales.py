"""Generate one persona per bundled locale to show global coverage.

Run with:  uv run python examples/global_locales.py
"""

from __future__ import annotations

from persona_factory import PersonaFactory, available_locales


def main() -> None:
    print(f"{'locale':<8} {'script':<12} {'name':<22} age  occupation")
    print("-" * 70)
    for locale in available_locales():
        person = PersonaFactory(locale, seed=7).generate()
        print(
            f"{locale:<8} "
            f"{person.identity.script or '':<12} "
            f"{person.display_name:<22} "
            f"{person.identity.age:>3}  "
            f"{person.socioeconomic.occupation}"
        )


if __name__ == "__main__":
    main()
