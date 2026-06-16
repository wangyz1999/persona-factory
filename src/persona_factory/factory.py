"""The :class:`PersonaFactory` — the single high-level entrypoint.

Generation is two-phase:

1. **Sample** every enabled domain independently, in dependency order, each with
   its own derived RNG sub-stream so toggling one domain does not perturb others.
2. **Resolve cross-domain key-links** — the small fixed set of coherence rules
   that span domains (e.g. occupation -> income-band sanity clamp). Intra-domain
   links (name<->gender, age<->generation) live inside the relevant generator.

There is intentionally no general correlation engine; only these explicit links.
"""

from __future__ import annotations

import random
from typing import Any

import persona_factory.generators  # noqa: F401  (registers built-in generators)
from persona_factory.config import AttributeSpec, PersonaConfig
from persona_factory.data import available_locales, load_locale
from persona_factory.exceptions import InvalidOverrideError
from persona_factory.generators.base import get_registry, ordered_domains
from persona_factory.keylinks import apply_cross_domain_links
from persona_factory.models.persona import Persona
from persona_factory.rng import RNG

# Override keyword -> dotted attribute path. Lets callers write
# ``factory.generate(gender="female", mbti="INTJ")`` instead of nested specs.
_OVERRIDE_ALIASES: dict[str, str] = {
    "gender": "identity.gender",
    "given_name": "identity.given_name",
    "family_name": "identity.family_name",
    "pronouns": "identity.pronouns",
    "age": "identity.age",
    "occupation": "socioeconomic.occupation",
    "education_level": "socioeconomic.education_level",
    "income_band": "socioeconomic.income_band",
    "mbti": "personality.mbti",
    "enneagram": "personality.enneagram_type",
    "religion": "beliefs.religion",
    "political_orientation": "beliefs.political_orientation",
    "diet": "lifestyle.diet",
    "tone": "communication.tone",
    "formality": "communication.formality",
}


class PersonaFactory:
    """Generate coherent fake personas, individually or in pools.

    Parameters
    ----------
    locale:
        A bundled locale code (e.g. ``"en_US"``, ``"ja_JP"``). See
        :func:`persona_factory.data.available_locales`.
    seed:
        Reproducibility seed. The same seed + config always yields the same
        persona.
    config:
        A :class:`PersonaConfig`. If omitted, a default is built from ``locale``
        and ``seed``.
    """

    def __init__(
        self,
        locale: str = "en_US",
        seed: int | str | None = None,
        config: PersonaConfig | None = None,
    ) -> None:
        if config is None:
            config = PersonaConfig(locale=locale, seed=seed)
        else:
            # explicit args win over config defaults when provided
            if locale != "en_US":
                config = config.model_copy(update={"locale": locale})
            if seed is not None:
                config = config.model_copy(update={"seed": seed})
        self.config = config
        if self.config.locale not in available_locales():
            from persona_factory.exceptions import UnknownLocaleError

            raise UnknownLocaleError(self.config.locale, list(available_locales()))

    # -- single persona --------------------------------------------------
    def generate(self, seed: int | str | None = None, **overrides: Any) -> Persona:
        """Generate one :class:`Persona`.

        Keyword overrides pin attributes before sampling, e.g.::

            factory.generate(gender="female", age=30, mbti="INTJ")

        ``include=[...]`` / ``exclude=[...]`` select domains for this call only.
        """
        config = self._config_with_overrides(overrides)
        effective_seed = seed if seed is not None else config.seed
        if effective_seed is None:
            # No seed requested: draw a concrete one from system entropy so each
            # call truly randomizes. We must materialize it (rather than pass
            # ``None`` straight through) because ``RNG.derive`` keys child streams
            # off the parent seed -- a ``None`` parent yields a fixed "None:domain"
            # label and therefore the *same* persona every run. Recording the
            # drawn seed in ``meta`` keeps the result reproducible after the fact.
            effective_seed = random.SystemRandom().getrandbits(64)
        rng = RNG(effective_seed)
        locale_data = load_locale(config.locale, "data.json")

        persona = Persona()
        registry = get_registry()
        enabled = [d for d in config.enabled_domains() if d in registry]
        for domain in ordered_domains(enabled):
            generator = registry[domain]
            sub_rng = rng.derive(domain)
            generator.generate(sub_rng, config, persona, locale_data)

        apply_cross_domain_links(persona, rng.derive("_keylinks"), config, locale_data)

        persona.meta = {
            "locale": config.locale,
            "seed": effective_seed,
            "reference_year": config.reference_year,
            "domains": ordered_domains(enabled),
        }
        return persona

    # -- pools -----------------------------------------------------------
    def generate_pool(
        self,
        n: int,
        distributions: dict[str, dict[Any, float]] | None = None,
        seed: int | str | None = None,
    ) -> Any:
        """Generate a :class:`~persona_factory.pools.population.PersonaPool`.

        ``distributions`` maps an override keyword (e.g. ``"gender"``) to a
        ``value -> proportion`` mapping that the pool will match in aggregate.
        """
        from persona_factory.pools.population import generate_pool

        return generate_pool(self, n, distributions=distributions, seed=seed)

    # -- internals -------------------------------------------------------
    def _config_with_overrides(self, overrides: dict[str, Any]) -> PersonaConfig:
        if not overrides:
            return self.config
        data = self.config.model_dump()
        attributes = dict(self.config.attributes)
        for key, value in overrides.items():
            if key in {"include", "exclude"}:
                data[key] = value
                continue
            if key == "age_range":
                low, high = value
                attributes["identity.age"] = AttributeSpec(min_value=low, max_value=high)
                continue
            path = _OVERRIDE_ALIASES.get(key, key)
            if "." not in path:
                raise InvalidOverrideError(
                    f"Unknown override {key!r}. Use a known alias "
                    f"({', '.join(sorted(_OVERRIDE_ALIASES))}) or a dotted path "
                    f"like 'identity.gender'."
                )
            attributes[path] = AttributeSpec(fixed=value)
        data["attributes"] = attributes
        return PersonaConfig.model_validate(data)
