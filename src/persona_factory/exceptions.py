"""Exception hierarchy for persona-factory.

All exceptions raised by the library derive from :class:`PersonaFactoryError`,
so callers can catch the whole family with a single ``except``.
"""

from __future__ import annotations


class PersonaFactoryError(Exception):
    """Base class for every error raised by persona-factory."""


class ConfigError(PersonaFactoryError):
    """Raised when a :class:`~persona_factory.config.PersonaConfig` is invalid."""


class UnknownLocaleError(PersonaFactoryError):
    """Raised when a requested locale has no bundled data."""

    def __init__(self, locale: str, available: list[str] | None = None) -> None:
        self.locale = locale
        self.available = available or []
        msg = f"No bundled data for locale {locale!r}."
        if self.available:
            msg += f" Available locales: {', '.join(sorted(self.available))}."
        super().__init__(msg)


class UnknownPresetError(PersonaFactoryError):
    """Raised when a requested preset name does not exist."""

    def __init__(self, name: str, available: list[str] | None = None) -> None:
        self.name = name
        self.available = available or []
        msg = f"Unknown preset {name!r}."
        if self.available:
            msg += f" Available presets: {', '.join(sorted(self.available))}."
        super().__init__(msg)


class DataError(PersonaFactoryError):
    """Raised when a bundled data file is missing or malformed."""


class EnrichmentError(PersonaFactoryError):
    """Raised when optional LLM enrichment fails or its extra is not installed."""


class InvalidOverrideError(PersonaFactoryError):
    """Raised when a generation override references an unknown attribute or bad value."""
