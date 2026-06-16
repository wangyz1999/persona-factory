# persona-factory

> Generate richly-attributed, coherent fake personas — and pools of them — for
> LLM agent roleplay, simulated users, and social simulation.

`persona-factory` is like [Faker](https://faker.readthedocs.io/), but for *whole
people*. Where Faker hands you a name or an address, persona-factory hands you a
**person**: demographics, body, multi-framework personality (OCEAN, MBTI,
Enneagram, DISC, …), values, beliefs, lifestyle, communication style, and a
short narrative — all internally consistent and ready to drop straight into an
LLM system prompt.

- **Coherent, not random** — a persona's name matches their gender and locale,
  their pronouns match their gender, their generation matches their age, their
  income stays plausible for their occupation.
- **Globally inclusive** — 12 bundled locales spanning Latin, Cyrillic, Han,
  Japanese, Arabic, and Devanagari scripts. Adding a locale is pure data.
- **Highly configurable** — fix any attribute, constrain ranges, supply weighted
  distributions, or enable/disable whole attribute domains.
- **Reproducible** — every persona is seeded; the same seed always yields the
  same person.
- **LLM-ready** — render to a system prompt, a markdown card, or JSON/JSONL.
- **Typed & dependency-light** — pydantic v2 core, fully type-checked, no Faker
  dependency. All data is bundled.

## Install

```bash
pip install persona-factory
# optional extras:
pip install "persona-factory[enrichment]"  # LLM backstory enrichment (anthropic)
pip install "persona-factory[polars]"      # PersonaPool.to_dataframe()
pip install "persona-factory[yaml]"        # load configs from YAML
```

## Quickstart

```python
from persona_factory import PersonaFactory

factory = PersonaFactory(locale="en_US", seed=42)
person = factory.generate(gender="female", age_range=(25, 35), mbti="INTJ")

print(person.display_name)            # e.g. "Jamie Clark"
print(person.to_system_prompt())      # second-person LLM instruction
print(person.to_markdown_card())      # human-readable card
data = person.to_dict()               # plain dict / JSON-serializable
```

### A pool that matches target distributions

```python
pool = factory.generate_pool(
    1000,
    distributions={"gender": {"female": 0.5, "male": 0.48, "non_binary": 0.02}},
)
pool.counts("identity.gender")        # {'female': 500, 'male': 480, 'non_binary': 20}
pool.to_jsonl()                       # one persona per line
pool.to_dataframe()                   # polars DataFrame (with [polars] extra)
```

### Presets

```python
from persona_factory import PersonaFactory, presets

factory = PersonaFactory(config=presets.get("gen_z_global"))
person = factory.generate()
```

Bundled presets: `realistic_us_adult`, `gen_z_global`, `enterprise_personas`,
`minimal_identity`, `full_dossier`, `elderly_retiree`.

### Optional: enrich with Claude

```python
from persona_factory import PersonaFactory
from persona_factory.enrichment import enrich   # needs the [enrichment] extra

person = PersonaFactory("en_US", seed=42).generate()
enrich(person, backstory=True, sample_dialogue=True)  # uses ANTHROPIC_API_KEY
print(person.narrative.backstory)
```

## CLI

```bash
persona-factory generate --seed 42 --format card
persona-factory generate --set gender=female --set mbti=INTJ --format prompt
persona-factory pool --n 100 --out people.jsonl
persona-factory locales        # list bundled locales
persona-factory presets        # list bundled presets
persona-factory schema         # dump the Persona JSON schema
```

## What's in a persona?

Thirteen optional attribute domains (request any subset via `include=`/`exclude=`):

| Domain | Examples |
| --- | --- |
| **identity** | name, gender, pronouns, age, DOB, generation, nationality, languages, locale/script |
| **physical** | height, weight, body type, eye/hair/skin, handedness, blood type, voice |
| **contact** | email, phone, username, social handles, device, avatar seed |
| **location** | address, city/region/country, postal code, timezone, coordinates |
| **socioeconomic** | occupation, industry, education, seniority, income band, social class |
| **personality** | OCEAN scores, MBTI, Enneagram (+wing), DISC, temperament, traits |
| **values** | core values, moral foundations, character strengths |
| **beliefs** | religion + religiosity, political orientation, worldview |
| **lifestyle** | hobbies, interests, diet, fitness, substances, chronotype, tech savviness |
| **social** | marital status, orientation, children, siblings |
| **communication** | tone, formality, verbosity, humor, emoji usage, accent, catchphrases |
| **narrative** | goals, fears, motivations, quirks, life events, bio |
| **documents** | clearly-synthetic national ID / card / IBAN / plate (opt-in) |

See [`PLAN.md`](PLAN.md) for the full design and [`examples/`](examples/) for
runnable scripts.

## How coherence works

Attributes are sampled independently, then a small fixed set of **key-link
resolvers** enforce the relationships that matter: `gender + locale → name`,
`gender → pronouns`, `age → generation → DOB`, `occupation → income band`
(sanity clamp), and minor-age safety clamps. There is no general correlation
engine — just these explicit links — which keeps generation fast and
predictable.

## Configuration

```python
from persona_factory import PersonaConfig, AttributeSpec, PersonaFactory

config = PersonaConfig(
    locale="de_DE",
    seed=7,
    exclude=["documents"],
    attributes={
        "identity.age": AttributeSpec(min_value=30, max_value=45),
        "beliefs.religion": AttributeSpec(
            choices=["christianity", "none"], weights=[0.6, 0.4]
        ),
    },
)
person = PersonaFactory(config=config).generate()
```

Configs also load from dict/JSON/YAML via `PersonaConfig.from_dict` /
`PersonaConfig.from_file`.

## Development

```bash
uv sync --extra all       # install with dev tooling + all extras
uv run pytest             # run tests
uv run ruff check .       # lint
uv run mypy src           # type-check
```

## License

MIT
