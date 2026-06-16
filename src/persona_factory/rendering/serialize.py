"""Serialization helpers (dict / JSON / JSONL).

Thin wrappers over pydantic so callers have one import surface; the ``Persona``
model also exposes :meth:`~persona_factory.models.persona.Persona.to_dict` and
``to_json`` directly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable

    from persona_factory.models.persona import Persona


def to_dict(persona: Persona, *, exclude_none: bool = True) -> dict[str, Any]:
    return persona.model_dump(exclude_none=exclude_none, mode="json")


def to_json(persona: Persona, *, exclude_none: bool = True, indent: int | None = 2) -> str:
    return persona.model_dump_json(exclude_none=exclude_none, indent=indent)


def to_jsonl(personas: Iterable[Persona], *, exclude_none: bool = True) -> str:
    """Render an iterable of personas as newline-delimited JSON."""
    return "\n".join(p.model_dump_json(exclude_none=exclude_none, indent=None) for p in personas)
