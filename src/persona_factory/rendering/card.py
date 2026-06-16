"""Render a persona as a human-readable Markdown card.

Unlike the system prompt (aimed at an LLM), the card is for humans reviewing or
documenting generated personas. It lays every populated domain out under
headings, skipping empty sections.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pydantic import BaseModel

    from persona_factory.models.persona import Persona

# Domain attribute -> heading, in display order.
_SECTIONS: list[tuple[str, str]] = [
    ("identity", "Identity"),
    ("physical", "Physical"),
    ("contact", "Contact"),
    ("location", "Location"),
    ("socioeconomic", "Work & Education"),
    ("personality", "Personality"),
    ("values", "Values"),
    ("beliefs", "Beliefs"),
    ("lifestyle", "Lifestyle"),
    ("social", "Relationships"),
    ("communication", "Communication"),
    ("narrative", "Narrative"),
    ("documents", "Documents (synthetic)"),
]


def render_card(persona: Persona, *, heading_level: int = 1) -> str:
    """Return a Markdown document describing ``persona``."""
    h = "#" * heading_level
    out: list[str] = [f"{h} {persona.display_name}"]

    for attr, title in _SECTIONS:
        section = getattr(persona, attr, None)
        if section is None:
            continue
        rows = list(_rows(section))
        if not rows:
            continue
        out.append(f"\n{h}# {title}\n")
        for label, value in rows:
            out.append(f"- **{label}:** {value}")

    return "\n".join(out) + "\n"


def _rows(model: BaseModel) -> Any:
    """Yield ``(label, formatted_value)`` for each populated field of a sub-model."""
    for name, value in model.__dict__.items():
        if value is None or value == [] or value == {}:
            continue
        if name == "big_five" and value is not None:
            yield "OCEAN", _format_ocean(value)
            continue
        if isinstance(value, list):
            if value and hasattr(value[0], "model_dump"):
                value = "; ".join(_flatten(item) for item in value)
            else:
                value = ", ".join(str(v) for v in value)
        elif hasattr(value, "model_dump"):
            value = _flatten(value)
        label = name.replace("_", " ").capitalize()
        yield label, value


def _format_ocean(big_five: Any) -> str:
    return (
        f"O={big_five.openness:.2f}, C={big_five.conscientiousness:.2f}, "
        f"E={big_five.extraversion:.2f}, A={big_five.agreeableness:.2f}, "
        f"N={big_five.neuroticism:.2f}"
    )


def _flatten(model: Any) -> str:
    parts = [f"{k}={v}" for k, v in model.__dict__.items() if v is not None]
    return "(" + ", ".join(parts) + ")"
