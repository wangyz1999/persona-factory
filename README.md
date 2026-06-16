<h1 align="center">🎭 persona-factory</h1>

<p align="center">
  <img width="1774" height="887" alt="persona-factory banner" src="https://github.com/user-attachments/assets/00fe95cf-f062-436b-9641-e7478400e640" />
</p>

<p align="center">
  <em>Generate richly-attributed, coherent fake personas — and pools of them —<br>
  for LLM agent roleplay, simulated users, and social simulation.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/persona-factory/"><img alt="PyPI" src="https://img.shields.io/pypi/v/persona-factory.svg"></a>
  <a href="https://pypi.org/project/persona-factory/"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/persona-factory.svg"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <a href="https://github.com/yunzhewa/persona-factory/actions"><img alt="CI" src="https://github.com/yunzhewa/persona-factory/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Typed" src="https://img.shields.io/badge/typed-pydantic%20v2-blue.svg">
  <img alt="Code style: ruff" src="https://img.shields.io/badge/style-ruff-261230.svg">
</p>


`persona-factory` generates *whole people*, not single fields. One call hands
you a **person**: demographics, body, multi-framework personality (OCEAN, MBTI,
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
- **Typed** — pydantic v2 models throughout, fully type-checked. All data is
  bundled, so core generation needs no network and no API key.

## Install

```bash
pip install persona-factory
```

A single install pulls in everything: persona generation, polars DataFrame
export, YAML config loading, and LLM enrichment via Anthropic, OpenAI, or
OpenRouter. Core generation still runs fully offline — you only need an API key
if you call `enrich()`.

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

## Example persona

One unedited persona — `PersonaFactory(locale="en_GB", seed=7).generate()`,
rendered with `.to_markdown_card()`. Every value is sampled from bundled data
with **no LLM**; note how name ↔ gender ↔ pronouns, age → Generation Z → DOB,
and occupation → income band all hang together.

<details>
<summary><strong>Alex Evans</strong> — 26, Tutor in Bristol, UK (click to expand)</summary>

```
# Alex Evans

## Identity
- Given name: Alex   Family name: Evans   Full name: Alex Evans
- Gender: male   Pronouns: he/him
- Age: 26   Date of birth: 1999-05-17   Generation: Generation Z
- Nationality: United Kingdom   Native language: English
- Locale: en_GB   Script: Latin

## Physical
- Height: 182.3 cm   Weight: 74.6 kg   Body type: curvy
- Eye color: amber   Hair: black, ponytail   Skin tone: tan
- Handedness: right   Blood type: O+   Voice: melodic
- Distinguishing features: a closely-cropped beard, heterochromia

## Location
- 484 Victoria Drive, Bristol, Yorkshire, United Kingdom (GB)
- Postal code: CX0 6YW   Timezone: Europe/London   Settlement: suburban

## Work & Education
- Occupation: Tutor (Education), junior, 4 yrs   Employment: full-time
- Education: associate, Sociology   Income band: lower_middle (GBP)
- Social class: lower_middle

## Personality
- OCEAN: O=0.38 C=0.86 E=0.70 A=0.66 N=0.23
- MBTI: ESFJ   Enneagram: 3 (3w2)   DISC: I   Temperament: guardian
- Traits: organized, reliable, goal-oriented, outgoing, energetic
- Strengths: witty, analytical, ambitious   Weaknesses: restless, easily distracted

## Beliefs
- Religion: none   Political orientation: left   Worldview: skeptical empiricist

## Lifestyle
- Hobbies: gardening, chess   Interests: finance, fashion, science
- Skills: coding, public speaking   Diet: omnivore   Fitness: moderately active
- Smoking: regularly   Alcohol: socially   Chronotype: night owl
- Favorite media: indie films, reality TV   Tech savviness: expert

## Relationships
- Marital status: single   Orientation: heterosexual
- Children: 1   Siblings: 1   Social circle: small

## Communication
- Tone: friendly   Formality: formal   Verbosity: rambling
- Vocabulary: academic   Humor: none   Emoji usage: moderate
- Accent: neutral   Dialect: code-switching

## Narrative
- Goals: achieve financial independence, travel the world
- Fears: running out of money, the unknown
- Motivations: proving themselves, curiosity
- Secrets: once dropped out of college
- Pet peeves: unsolicited advice   Quirks: never drinks coffee after noon
- Bio: Alex is a 26-year-old from United Kingdom who works as a Tutor in
  education. They come across as organized, reliable, goal-oriented. In their
  free time they enjoy gardening, chess.
```

</details>

### A pool that matches target distributions

```python
pool = factory.generate_pool(
    1000,
    distributions={"gender": {"female": 0.5, "male": 0.48, "non_binary": 0.02}},
)
pool.counts("identity.gender")        # {'female': 500, 'male': 480, 'non_binary': 20}
pool.to_jsonl()                       # one persona per line
pool.to_dataframe()                   # polars DataFrame
```

### Presets

```python
from persona_factory import PersonaFactory, presets

factory = PersonaFactory(config=presets.get("gen_z_global"))
person = factory.generate()
```

Bundled presets: `realistic_us_adult`, `gen_z_global`, `enterprise_personas`,
`minimal_identity`, `full_dossier`, `elderly_retiree`.

### Optional: enrich narrative with an LLM

Generation is fully offline. If you *also* want model-written prose (a vivid
bio, a first-person backstory, sample dialogue), call `enrich()` — the only part
of the library that touches the network.

```python
from persona_factory import PersonaFactory
from persona_factory.enrichment import enrich

person = PersonaFactory("en_US", seed=42).generate()

# Anthropic (default) — uses ANTHROPIC_API_KEY
enrich(person, backstory=True, sample_dialogue=True)

# OpenAI — uses OPENAI_API_KEY
enrich(person, provider="openai", model="gpt-4o")

# OpenRouter (any hosted model) — uses OPENROUTER_API_KEY
enrich(person, provider="openrouter", model="anthropic/claude-sonnet-4-6")

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

See [`examples/`](examples/) for runnable scripts.

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
uv sync                   # install with dev tooling
uv run pytest             # run tests
uv run ruff check .       # lint
uv run mypy src           # type-check
```

## License

MIT
