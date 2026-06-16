# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This repo is in the **bootstrap phase**: only a scaffold (`main.py` hello-world, near-empty `pyproject.toml`, Python pin) plus `PLAN.md` exist. The package described below does **not yet exist** — `PLAN.md` is the authoritative spec for what to build and the order to build it (§8 Build Order). Read `PLAN.md` before starting any implementation work; keep it in sync if the design changes.

## What this package is

`persona-factory` generates fake personas — or large pools of them — by template-based mix-and-matching of bundled data. Target use cases: LLM agent roleplay, simulated users, social simulation. Conceptually "Faker for whole identities": instead of one name/address, it produces a coherent, richly-attributed *person* (demographics, body, multi-framework personality, beliefs, lifestyle, communication style, narrative) that renders directly into an LLM system prompt.

## Architecture (target — see PLAN.md for detail)

The design hinges on a few decisions that are not obvious from any single file:

- **Data is bundled, not pulled from Faker.** All names/locales/occupations/lexicons live as JSON under `src/persona_factory/data/`, loaded via `importlib.resources` (must work from a zipped/installed wheel, not just the source tree). Adding a locale should be a pure-data change, not a code change. **No Faker dependency.**
- **`src/` layout is deliberate** — imports must resolve only against the installed package, so always test against an installed/editable install, not relative imports from the repo root.
- **Generation is two-phase.** Per-domain generators in `generators/` sample attributes *independently*; then `factory.py` applies a small fixed set of **key-link resolvers** in order to enforce coherence: `gender+locale→name`, `gender→pronouns`, `age→generation→DOB`, `occupation→income-band` sanity clamp, `locale→country/language/script`. There is intentionally **no general correlation engine** — only these hard-coded links.
- **`PersonaFactory` is the single entrypoint.** `PersonaFactory(locale=, seed=, config=)` → `.generate(**overrides)` and `.generate_pool(n, distributions=)`. Overrides pin or constrain attributes *before* sampling.
- **Reproducibility is a hard requirement.** All randomness flows through the seeded RNG wrapper in `rng.py`; same seed must produce byte-identical output. Never call `random`/`Math.random`-style globals directly in generators.
- **Pydantic v2 models** (`models/persona.py`) are the spine — nested sub-models per domain, **every field optional** (users request subsets). Serialization and JSON-schema export come from pydantic.
- **Rendering and enrichment are separate layers.** `rendering/` turns a `Persona` into a system prompt / markdown card / JSON offline. `enrichment/claude.py` is *optional* (lazy-imports `anthropic`, guarded behind the `enrichment` extra) and calls Claude only to fill freeform fields. Core generation must never require an API key or network.

## Commands

The toolchain is finalized in `PLAN.md §5` (hatchling build, pydantic core dep, dev extra with pytest/ruff/mypy). Once `pyproject.toml` is set up:

```bash
pip install -e ".[dev]"          # editable install with dev tooling
pytest                           # run all tests
pytest tests/test_identity.py    # run one test file
pytest -k "reproducib"           # run tests matching an expression
ruff check .                     # lint
mypy src                         # type-check
python -m build                  # build wheel/sdist
```

Verify bundled data ships correctly by installing the built wheel in a fresh venv and generating a persona (data-file packaging is the most common breakage). See `PLAN.md §9` for the full end-to-end verification checklist.

## Conventions

- **Python floor is `>=3.10`** (the current `>=3.14` pin in `pyproject.toml` must be lowered — it severely limits adoption).
- When adding an attribute: extend the pydantic model (optional field) **and** its generator **and** any backing JSON data **and** tests — these move together.

## Committing

Commit as you go in meaningful, self-contained units — one logical change per commit (code + its doc/data update together), never a giant catch-all. Stage deliberately with explicit `git add <paths>`; avoid `git add -A`/`git add .`. Never stage build artifacts, `output/`, or `.venv/`. Only commit when the slice builds/runs.

Follow **Conventional Commits 1.0.0**: `<type>[optional scope]: <description>` where type ∈ `feat|fix|docs|chore|refactor|test|build`. Use the body to explain *why*. Mark breaking changes with `!` after the type/scope or a `BREAKING CHANGE:` footer.
