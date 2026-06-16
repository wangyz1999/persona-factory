"""Command-line interface for persona-factory.

Subcommands::

    persona-factory generate [--locale ..] [--seed ..] [--format ..] [overrides]
    persona-factory pool --n N [--locale ..] [--seed ..] [--format jsonl] [--out FILE]
    persona-factory locales        # list bundled locales
    persona-factory presets        # list bundled presets
    persona-factory schema         # dump the Persona JSON schema

Implemented with the standard-library :mod:`argparse` so the CLI adds no extra
dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from persona_factory import presets
from persona_factory.config import PersonaConfig
from persona_factory.data import available_locales
from persona_factory.factory import PersonaFactory
from persona_factory.models.persona import Persona

_FORMATS = ("prompt", "card", "json")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="persona-factory",
        description="Generate richly-attributed, coherent fake personas.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- generate ----------------------------------------------------------
    gen = sub.add_parser("generate", help="generate a single persona")
    _add_common(gen)
    gen.add_argument(
        "--format",
        choices=_FORMATS,
        default="card",
        help="output format (default: card)",
    )
    gen.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="override an attribute (e.g. --set gender=female --set mbti=INTJ)",
    )

    # -- pool --------------------------------------------------------------
    pool = sub.add_parser("pool", help="generate a pool of personas")
    _add_common(pool)
    pool.add_argument("--n", type=int, required=True, help="number of personas")
    pool.add_argument(
        "--format",
        choices=("jsonl", "json"),
        default="jsonl",
        help="output format (default: jsonl)",
    )
    pool.add_argument("--out", help="write output to this file instead of stdout")

    # -- info commands -----------------------------------------------------
    sub.add_parser("locales", help="list bundled locales")
    sub.add_parser("presets", help="list bundled presets")
    sub.add_parser("schema", help="print the Persona JSON schema")

    return parser


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--locale", default="en_US", help="locale code (default: en_US)")
    p.add_argument("--seed", help="reproducibility seed (int or string)")
    p.add_argument("--preset", help="start from a bundled preset config")


def _coerce_seed(raw: str | None) -> int | str | None:
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return raw


def _parse_overrides(pairs: list[str]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"invalid --set {pair!r}; expected KEY=VALUE")
        key, value = pair.split("=", 1)
        overrides[key.strip()] = _coerce_value(value.strip())
    return overrides


def _coerce_value(value: str) -> Any:
    for caster in (int, float):
        try:
            return caster(value)
        except ValueError:
            continue
    return value


def _make_factory(args: argparse.Namespace) -> PersonaFactory:
    seed = _coerce_seed(args.seed)
    if getattr(args, "preset", None):
        config: PersonaConfig = presets.get(args.preset)
        if args.locale != "en_US":
            config = config.model_copy(update={"locale": args.locale})
        if seed is not None:
            config = config.model_copy(update={"seed": seed})
        return PersonaFactory(config=config)
    return PersonaFactory(locale=args.locale, seed=seed)


def _render(persona: Persona, fmt: str) -> str:
    if fmt == "prompt":
        return persona.to_system_prompt()
    if fmt == "card":
        return persona.to_markdown_card()
    return persona.to_json()


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "locales":
        print("\n".join(available_locales()))
        return 0
    if args.command == "presets":
        print("\n".join(presets.names()))
        return 0
    if args.command == "schema":
        print(json.dumps(Persona.model_json_schema(), indent=2))
        return 0

    factory = _make_factory(args)

    if args.command == "generate":
        overrides = _parse_overrides(args.set)
        persona = factory.generate(**overrides)
        print(_render(persona, args.format))
        return 0

    if args.command == "pool":
        pool = factory.generate_pool(args.n)
        if args.format == "jsonl":
            output = pool.to_jsonl()
        else:
            output = json.dumps(pool.to_list(), ensure_ascii=False, indent=2)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(output + "\n")
            print(f"Wrote {len(pool)} personas to {args.out}", file=sys.stderr)
        else:
            print(output)
        return 0

    parser.error(f"unknown command {args.command!r}")  # pragma: no cover
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
