# Contributing to persona-factory

Thanks for your interest in improving persona-factory!

## Development setup

This project uses [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/yunzhewa/persona-factory
cd persona-factory
uv sync --extra all          # install with dev tooling + all optional extras
```

## Workflow

```bash
uv run pytest                # run the test suite
uv run pytest tests/test_identity.py   # a single file
uv run pytest -k reproducib  # tests matching an expression
uv run ruff check .          # lint
uv run ruff format .         # format
uv run mypy src              # type-check
```

All four (tests, ruff check, ruff format, mypy) must pass before a PR is merged;
CI enforces them on Python 3.10–3.13.

## Adding a locale

Locales are pure data — no code changes required. Create
`src/persona_factory/data/locales/<code>/data.json` mirroring an existing locale
(e.g. `en_US`), with gender-partitioned `given_names`, `surnames`, `cities`,
`regions`, address/postal/phone format masks, `currency`, `timezones`, and
`script`. Set `"name_order": "family_first"` for locales that put the family
name first. The data-integrity test will automatically cover the new locale.

## Adding an attribute

An attribute change usually touches four places that move together:

1. the pydantic model in `models/persona.py` (add an **optional** field, plus an
   enum in `models/enums.py` if it's a closed set);
2. the relevant generator in `generators/`;
3. any backing JSON under `data/`;
4. tests.

All randomness must flow through the injected `RNG` (never the global `random`),
and the field must be optional so existing callers are unaffected.

## Commit style

Follow [Conventional Commits](https://www.conventionalcommits.org/) — e.g.
`feat(generators): ...`, `fix: ...`, `docs: ...`. Keep commits to one logical
change.
