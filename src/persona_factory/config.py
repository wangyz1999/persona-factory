"""Configuration for persona generation.

A :class:`PersonaConfig` controls:

* which attribute domains are generated (``include`` / ``exclude``),
* per-attribute constraints via :class:`AttributeSpec` (fix a value, restrict to
  weighted choices, or bound a numeric range),
* locale selection / weighting,
* the RNG seed.

Configs are plain pydantic models, so they load from dicts, JSON or YAML and
validate on construction.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from persona_factory.exceptions import ConfigError

#: Every attribute domain known to the factory, in a sensible default order.
ALL_DOMAINS: tuple[str, ...] = (
    "identity",
    "physical",
    "contact",
    "location",
    "socioeconomic",
    "personality",
    "values",
    "beliefs",
    "lifestyle",
    "social",
    "communication",
    "narrative",
    "documents",
)

#: Domains enabled when the caller does not specify otherwise.
DEFAULT_DOMAINS: tuple[str, ...] = (
    "identity",
    "physical",
    "location",
    "socioeconomic",
    "personality",
    "beliefs",
    "lifestyle",
    "social",
    "communication",
    "narrative",
)


class AttributeSpec(BaseModel):
    """A per-attribute constraint applied before random sampling.

    Exactly one mode is active:

    * ``fixed`` — always use this value;
    * ``choices`` (+ optional ``weights``) — sample from this set only;
    * ``min_value`` / ``max_value`` — clamp a numeric attribute's range.
    """

    model_config = ConfigDict(extra="forbid")

    fixed: Any = None
    choices: list[Any] | None = None
    weights: list[float] | None = None
    min_value: float | None = None
    max_value: float | None = None

    @model_validator(mode="after")
    def _check(self) -> AttributeSpec:
        if self.weights is not None:
            if self.choices is None:
                raise ValueError("weights given without choices")
            if len(self.weights) != len(self.choices):
                raise ValueError("weights and choices must be the same length")
        if (
            self.min_value is not None
            and self.max_value is not None
            and self.min_value > self.max_value
        ):
            raise ValueError("min_value must be <= max_value")
        return self


class PersonaConfig(BaseModel):
    """Top-level generation configuration."""

    model_config = ConfigDict(extra="forbid")

    locale: str = "en_US"
    #: Optional weighting over multiple locales for pool generation.
    locale_weights: dict[str, float] | None = None
    seed: int | str | None = None

    include: list[str] | None = None
    exclude: list[str] = Field(default_factory=list)

    #: Map of dotted attribute path (e.g. ``"identity.gender"``) -> spec.
    attributes: dict[str, AttributeSpec] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_domains(self) -> PersonaConfig:
        known = set(ALL_DOMAINS)
        for name in (self.include or []) + self.exclude:
            if name not in known:
                raise ConfigError(
                    f"Unknown domain {name!r}. Known domains: {', '.join(ALL_DOMAINS)}"
                )
        return self

    # -- derived ---------------------------------------------------------
    def enabled_domains(self) -> list[str]:
        """Resolve ``include``/``exclude`` into the final domain list."""
        base = list(self.include) if self.include is not None else list(DEFAULT_DOMAINS)
        excluded = set(self.exclude)
        return [d for d in base if d not in excluded]

    def spec_for(self, path: str) -> AttributeSpec | None:
        """Return the :class:`AttributeSpec` for a dotted attribute path, if any."""
        return self.attributes.get(path)

    # -- loading ---------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PersonaConfig:
        return cls.model_validate(data)

    @classmethod
    def from_file(cls, path: str | Path) -> PersonaConfig:
        """Load a config from a ``.json``, ``.yaml`` or ``.yml`` file."""
        p = Path(path)
        text = p.read_text(encoding="utf-8")
        if p.suffix in {".yaml", ".yml"}:
            import yaml  # type: ignore[import-untyped]

            data = yaml.safe_load(text)
        else:
            data = json.loads(text)
        return cls.from_dict(data)
