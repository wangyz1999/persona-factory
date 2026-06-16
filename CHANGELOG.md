# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-16

### Added
- Initial release.
- `PersonaFactory` entrypoint: `generate()` and `generate_pool()`.
- Thirteen optional attribute domains (identity, physical, contact, location,
  socioeconomic, personality, values, beliefs, lifestyle, social,
  communication, narrative, documents).
- Multi-framework personality: OCEAN, MBTI (derived from OCEAN or pinned),
  Enneagram + wing, DISC, temperament.
- 12 bundled locales spanning Latin, Cyrillic, Han, Japanese, Arabic, and
  Devanagari scripts.
- Cross-domain key-link resolvers for coherence (name↔gender↔locale,
  pronouns↔gender, age↔generation↔DOB, occupation→income clamp).
- Seeded, fully reproducible generation.
- `PersonaConfig` + `AttributeSpec` (fixed / weighted-choices / numeric range);
  loads from dict / JSON / YAML.
- Six bundled presets.
- Distribution-aware `PersonaPool` with `to_jsonl` / `to_dataframe` (polars).
- Rendering to LLM system prompt (`roleplay` / `profile` styles) and markdown.
- `persona-factory` CLI (`generate` / `pool` / `locales` / `presets` /
  `schema`).
- Optional Claude-backed narrative enrichment (`[enrichment]` extra).
