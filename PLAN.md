# Persona Factory — Build Plan

## Context

`persona-factory` will be a pip-installable Python package that **generates fake personas — or large pools of them — via highly configurable template-based mix-and-matching**. The target audience is people building LLM agent roleplay, simulated users, and social simulations, where you need many *coherent, richly-attributed* synthetic humans.

Think of it as "Faker, but for whole identities": Faker gives you a name or an address; Persona Factory gives you a *person* — name, demographics, body, psychology (multiple personality frameworks), beliefs, lifestyle, communication style, backstory — that hangs together and renders straight into an LLM system prompt.

The repo today is an empty `uv`-style scaffold (`main.py` hello-world, empty `pyproject.toml`, `requires-python >=3.14`). This plan takes it to a structured, documented, tested, publishable package.

### Confirmed design decisions
- **Data model & data:** `pydantic` v2 as a core dependency; **bundle ALL data ourselves** (names, locales, occupations, etc.) — no Faker dependency. Full control over global coverage.
- **Coherence:** **Independent sampling + a small set of hard-coded key links** (name↔gender↔locale, pronouns↔gender, age↔generation↔DOB, occupation→income-band sanity). Not a full correlation engine.
- **LLM integration:** **Render-only by default** (templates → system prompt / markdown / JSON), **plus an optional `enrichment` module** that calls Claude to flesh out freeform backstory/dialogue. The `anthropic` SDK is an optional extra.
- **Python floor:** `>=3.10` (publishable reach; modern typing).

### Guiding principles
1. **Comprehensive taxonomy** — cover every category that meaningfully describes/influences a human (see §2).
2. **Globally inclusive** — locale-driven data so the name/identity generators can in principle represent any human on earth.
3. **Configurable at every level** — fix any attribute, constrain ranges, supply custom distributions, enable/disable whole attribute modules.
4. **Convenient API** — one obvious entrypoint (`PersonaFactory`), sensible defaults, reproducible via `seed`.
5. **Publishable** — clean structure, typed (`py.typed`), tested, documented, CI, semver.

---

## 1. Package Layout

```
persona-factory/
├── pyproject.toml              # rewritten: metadata, deps, extras, build, tooling
├── README.md                   # quickstart + feature tour
├── LICENSE                     # MIT
├── CHANGELOG.md
├── CONTRIBUTING.md
├── PLAN.md                     # this plan
├── mkdocs.yml                  # docs site config
├── docs/                       # usage, attribute reference, locale guide, cookbook
├── examples/                   # runnable scripts (single, pool, simulation, enrichment)
├── tests/
└── src/
    └── persona_factory/
        ├── __init__.py         # public API surface
        ├── py.typed
        ├── exceptions.py
        ├── rng.py              # seeded RNG wrapper (reproducibility)
        ├── factory.py          # PersonaFactory orchestrator + key-link resolution
        ├── config.py           # PersonaConfig, AttributeSpec, presets loader
        ├── cli.py              # `persona-factory` CLI (stdlib argparse)
        ├── models/
        │   ├── persona.py      # Persona root model + nested sub-models
        │   └── enums.py        # Gender, Pronouns, Generation, etc.
        ├── generators/
        │   ├── base.py         # Generator protocol/ABC + registry
        │   ├── identity.py     # names, gender, sex, age, dob, ethnicity, nationality
        │   ├── physical.py     # height, weight, build, hair/eye/skin, handedness…
        │   ├── contact.py      # email, phone, username, social handles, avatar seed
        │   ├── location.py     # address, city/region/country, postal, tz, coords
        │   ├── socioeconomic.py# occupation, industry, education, income band, class
        │   ├── personality.py  # OCEAN, MBTI, Enneagram, DISC, HEXACO, temperament
        │   ├── values.py       # Schwartz values, moral foundations, VIA strengths
        │   ├── beliefs.py      # religion/religiosity, political orientation
        │   ├── lifestyle.py    # hobbies, diet, health, substances, chronotype, tech
        │   ├── social.py       # relationship/marital status, family, orientation
        │   ├── communication.py# tone, formality, verbosity, humor, emoji, dialect
        │   └── narrative.py    # goals, fears, motivations, quirks, life events
        ├── pools/
        │   └── population.py    # generate_pool(), distribution sampling, cohorts
        ├── rendering/
        │   ├── system_prompt.py # → LLM system prompt
        │   ├── card.py          # → markdown persona card
        │   └── serialize.py     # → dict / json / jsonl
        ├── enrichment/
        │   └── claude.py        # OPTIONAL: enrich() via anthropic SDK
        └── data/                # bundled datasets (packaged via importlib.resources)
            ├── locales/<locale>/{given_names,surnames,...}.json
            ├── personality/{mbti,enneagram,ocean_facets,...}.json
            ├── occupations/{taxonomy,income_bands}.json
            └── lexicons/{hobbies,values,communication,...}.json
```

`src/` layout is used so imports resolve only against the installed package (avoids the classic "works in repo, breaks installed" trap). `main.py` is deleted.

---

## 2. Persona Attribute Taxonomy

The heart of the package. Modeled as nested pydantic sub-models on the root `Persona`; **every field is optional** so users can request subsets. Grouped by domain:

**A. Identity / Demographics** — given/middle/family name, full name, nickname, prefix/suffix; gender identity, sex assigned at birth, pronouns (incl. neopronouns); age, date of birth, generation; nationality, ethnicity/ancestry, race; native + spoken languages with proficiency; locale/script (Latin, Cyrillic, CJK, Arabic, Devanagari, …).

**B. Physical** — height, weight, build/body type; eye/hair/skin descriptors, hair style; handedness, blood type; disabilities/accessibility needs; distinguishing features; voice qualities.

**C. Contact / Digital** — email, phone, username/handle, fake password; social profiles; IP/user-agent/device; avatar seed.

**D. Location / Geography** — street address, city, region/state, country, postal code, lat/long; timezone; urban/suburban/rural.

**E. Socioeconomic** — occupation, job title, industry, employer, seniority, years of experience; education level, field, institution; income band, net-worth tier, socioeconomic class; employment status.

**F. Personality (multi-framework, all configurable & independently selectable)** — Big Five / OCEAN (+ facets, numeric scores), MBTI (16 types), Enneagram (type + wing + tritype), DISC, HEXACO, Keirsey/temperament, dominant cognitive & learning style.

**G. Values & Character** — Schwartz basic values, Moral Foundations, VIA character strengths, core attitudes.

**H. Beliefs / Culture** — religion/spirituality + religiosity level, political orientation/affiliation, broad worldview.

**I. Lifestyle / Behavioral** — hobbies, interests, skills; diet + allergies; health/fitness; substance use (smoking/alcohol); chronotype/sleep; media tastes; shopping/brand affinity; tech-savviness.

**J. Social / Relationships** — relationship & marital status, sexual orientation, children/siblings/parents, social-network size.

**K. Communication style (critical for roleplay)** — tone, formality, verbosity, vocabulary level, humor style, emoji usage, accent/dialect, catchphrases, typing quirks.

**L. Narrative / Psychology** — goals, fears, motivations, secrets, pet peeves, quirks, notable life events, short bio.

**M. Identity documents (Faker-parity, clearly fake)** — national-ID-shaped string, credit card (test ranges), IBAN/account, license plate, passport-shaped — all explicitly synthetic, never real-format-valid where that risks misuse.

> The attribute reference (§2) ships as a generated docs page so users can see every field, its type, and which generator/data backs it.

---

## 3. Core Components

### 3.1 Data models (`models/persona.py`, `models/enums.py`)
- `Persona` pydantic root model with nested sub-models (`Identity`, `Physical`, `Personality`, `CommunicationStyle`, …) mirroring §2 domains. All fields optional.
- Rich enums for closed sets (`Gender`, `PronounSet`, `Generation`, `MBTIType`, `Enneagram`, `EducationLevel`, …); free-ish fields use `str`/typed aliases.
- Built-in `model_dump`, `model_dump_json`, JSON-schema export come free from pydantic.

### 3.2 Generators (`generators/`)
- `base.py`: `Generator` protocol — `generate(rng, config, partial) -> dict`. A registry maps domain → generator so modules can be toggled. Each generator reads bundled data via `importlib.resources` and the seeded `rng`.
- One module per domain. Personality module houses sub-generators per framework (OCEAN scores → derived MBTI letters optional, etc.).

### 3.3 Factory & key-links (`factory.py`)
- `PersonaFactory(locale=..., seed=..., config=...)`.
- `.generate(**overrides) -> Persona`: runs enabled generators independently, then applies **key-link resolvers** in a fixed order:
  - `gender + locale → given/family name` (name pools are gender- & locale-partitioned)
  - `gender → pronouns` (overridable)
  - `age → generation`, `age → date_of_birth`
  - `occupation_category → income band` (sanity clamp only)
  - `locale → country/language/script` defaults
- Overrides (`gender="female"`, `age_range=(25,35)`, `mbti="INTJ"`, `include=[...]`, `exclude=[...]`) pin or constrain before sampling.

### 3.4 Config & presets (`config.py`)
- `PersonaConfig` pydantic model: which domains enabled, per-attribute `AttributeSpec` (fixed value | choices+weights | numeric range/distribution), locale weighting, RNG seed.
- Load from dict / YAML / JSON (`PersonaConfig.from_file`).
- Bundled presets: `realistic_us_adult`, `gen_z_global`, `enterprise_personas`, `minimal_identity`, etc.

### 3.5 Pools / populations (`pools/population.py`)
- `factory.generate_pool(n, distributions=None, cohorts=None) -> PersonaPool`.
- Distribution-aware sampling so a 1,000-person pool can match target gender/age/locale splits.
- `PersonaPool` helpers: `to_jsonl()`, `to_dataframe()` (optional `pandas` extra), filtering, stats summary, uniqueness guarantees on identity fields.

### 3.6 Rendering (`rendering/`)
- `persona.to_system_prompt(style=...)` → second-person LLM instruction ("You are …").
- `persona.to_markdown_card()` → human-readable card.
- `persona.to_dict()/.to_json()/.to_jsonl()`; pool-level equivalents.
- Templates are data-driven and overridable.

### 3.7 Optional enrichment (`enrichment/claude.py`)
- `enrich(persona, *, backstory=True, sample_dialogue=False, model="claude-sonnet-4-6", client=None)`.
- Imports `anthropic` lazily; raises a clear error if the `enrichment` extra isn't installed.
- Builds a prompt from the structured persona, calls Claude, writes freeform fields (`bio`, `backstory`, `sample_dialogue`) back onto the model. Default model `claude-sonnet-4-6`; `claude-haiku-4-5` and `claude-opus-4-8` documented as alternatives. API key from `ANTHROPIC_API_KEY` or passed-in client. **Note:** before implementing this module, consult the `claude-api` skill to confirm current SDK call signatures/model IDs.

### 3.8 CLI (`cli.py`)
- `persona-factory generate --locale en_US --seed 42 --format card`
- `persona-factory pool --n 100 --format jsonl --out people.jsonl`
- `persona-factory schema` (dump JSON schema), `persona-factory presets`.
- Stdlib `argparse` to avoid extra deps.

### 3.9 Public API (`__init__.py`)
```python
from persona_factory import PersonaFactory, Persona, PersonaConfig, presets
factory = PersonaFactory(locale="en_US", seed=42)
p = factory.generate(gender="female", age_range=(25, 35), mbti="INTJ")
print(p.to_system_prompt())
pool = factory.generate_pool(1000, distributions={"gender": {"female": .5, "male": .48, "non_binary": .02}})
```

---

## 4. Bundled Data Strategy (`data/`)
- JSON datasets loaded via `importlib.resources` (works when zipped/installed).
- **Locales:** start with a meaningful spread across scripts/regions — e.g. `en_US`, `en_GB`, `es_ES/es_MX`, `fr_FR`, `de_DE`, `zh_CN`, `ja_JP`, `hi_IN`, `ar_SA`, `pt_BR`, `ru_RU`, `nb_NO` — each with gender-partitioned given names, surnames, and address/phone formats. Architecture makes adding locales pure data, not code.
- **Frameworks:** static reference data for MBTI/Enneagram/OCEAN facets/DISC/HEXACO descriptions; occupation taxonomy with income bands; lexicons for hobbies, values, communication traits, etc.
- Each dataset documents source/method and is clearly synthetic/aggregate (no real PII).
- A `data/README.md` + lightweight schema validation test guards dataset shape.

---

## 5. Packaging & Tooling (`pyproject.toml`)
- Backend: `hatchling` (clean `src/` + data-file inclusion).
- `requires-python = ">=3.10"` (replaces `>=3.14`).
- Core deps: `pydantic>=2`.
- Extras: `enrichment` → `anthropic`; `pandas` → `pandas`; `yaml` → `pyyaml`; `dev` → `pytest`, `pytest-cov`, `ruff`, `mypy`, `mkdocs-material`.
- Console script: `persona-factory = persona_factory.cli:main`.
- Include `py.typed` and bundle `data/**` as package data.
- Metadata: description, keywords (persona, faker, llm, agent, simulation, synthetic-data), classifiers, project URLs, MIT license.

---

## 6. Testing (`tests/`)
- Unit tests per generator (valid values, respects overrides, locale partitioning).
- **Reproducibility:** same seed → identical persona; different seed → different.
- **Coherence/key-link tests:** pronouns match gender, name pool matches gender+locale, generation matches age, DOB↔age consistent, income within occupation band.
- Config tests: fixed values honored, weighted choices respect distribution (statistical tolerance over large n), include/exclude toggles modules.
- Pool tests: size, distribution adherence, identity uniqueness, jsonl round-trip.
- Rendering tests: system prompt / card / json snapshots; schema export valid.
- Enrichment: mocked Anthropic client (no live API in CI).
- Data integrity test: every locale dir has required files with required keys.
- `pytest` + coverage gate; `ruff` + `mypy` in CI.

---

## 7. Documentation & Publishing
- `README.md`: pitch, install, 30-second quickstart, feature matrix, comparison to Faker, links to docs.
- `docs/` (MkDocs Material): Getting Started, Attribute Reference (auto-generated from models), Configuration & Presets, Locales, Pools & Simulation, LLM Rendering & Enrichment, Extending (custom generators/locales), API reference.
- `CHANGELOG.md` (Keep a Changelog), `CONTRIBUTING.md`, `LICENSE` (MIT).
- GitHub Actions: lint+type+test matrix (3.10–3.13), build, and a tag-triggered PyPI publish (Trusted Publishing/OIDC). Ship `0.1.0` once green.

---

## 8. Build Order (incremental, each step independently testable)
1. **Scaffold:** rewrite `pyproject.toml`, create `src/persona_factory/` tree, delete `main.py`, add `py.typed`, `exceptions.py`, `rng.py`, license.
2. **Models:** `enums.py` + `persona.py` (all sub-models, all optional).
3. **Data + identity generator:** seed a few locales; implement `identity.py`; wire `factory.generate()` with name/gender/age/pronoun/generation key-links. First end-to-end persona.
4. **Remaining generators** domain by domain (physical → contact → location → socioeconomic → personality → values → beliefs → lifestyle → social → communication → narrative), each with data + tests.
5. **Config & presets**, then **pools/population**.
6. **Rendering** (system prompt, card, serialize) + CLI.
7. **Optional enrichment** module (mocked tests).
8. **Docs site, examples, CI, CHANGELOG**; tag `0.1.0` and publish to PyPI.

---

## 9. Verification (end-to-end)
- `pip install -e .[dev]` then `pytest` (all green, coverage gate met).
- `python examples/single.py` → coherent persona prints as card + system prompt.
- `python examples/pool.py` → 1,000-persona JSONL with requested gender/age splits; verify distribution + identity uniqueness.
- `persona-factory generate --seed 42` twice → byte-identical output (reproducibility).
- `persona-factory schema` → valid JSON schema.
- `ruff check` and `mypy src` clean.
- Build artifact: `python -m build` → `pip install` the wheel in a fresh venv and import + generate (confirms bundled data ships correctly).
- Enrichment (manual, opt-in): with `ANTHROPIC_API_KEY` set and `[enrichment]` installed, `enrich(p)` populates `bio`/`backstory`.
