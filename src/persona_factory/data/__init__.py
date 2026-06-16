"""Bundled datasets and the loader that reads them via importlib.resources.

All data ships as JSON inside the installed wheel, so it must be accessed
through :func:`load_json` (which uses :mod:`importlib.resources`) rather than
filesystem paths — the latter break when the package is zip-imported.
"""

from __future__ import annotations

import json
from functools import cache
from importlib import resources
from typing import Any

from persona_factory.exceptions import DataError, UnknownLocaleError

_DATA_PKG = "persona_factory.data"


@cache
def load_json(*path_parts: str) -> Any:
    """Load and cache a JSON file bundled under ``persona_factory/data``.

    ``load_json("personality", "mbti.json")`` reads
    ``persona_factory/data/personality/mbti.json``. Results are cached, so the
    returned object must be treated as read-only.
    """
    try:
        resource = resources.files(_DATA_PKG)
        for part in path_parts:
            resource = resource / part
        text = resource.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError) as exc:
        raise DataError(f"Missing bundled data file: {'/'.join(path_parts)}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:  # pragma: no cover - guards corrupt data
        raise DataError(
            f"Malformed JSON in bundled data file {'/'.join(path_parts)}: {exc}"
        ) from exc


@cache
def available_locales() -> tuple[str, ...]:
    """Return the sorted tuple of locale codes that have bundled data."""
    locales_dir = resources.files(_DATA_PKG) / "locales"
    names = sorted(
        entry.name
        for entry in locales_dir.iterdir()
        if entry.is_dir() and not entry.name.startswith("_")
    )
    return tuple(names)


def load_locale(locale: str, filename: str) -> Any:
    """Load a JSON file for a specific locale, raising if the locale is unknown."""
    if locale not in available_locales():
        raise UnknownLocaleError(locale, list(available_locales()))
    return load_json("locales", locale, filename)
