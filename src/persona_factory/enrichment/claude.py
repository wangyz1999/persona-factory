"""Flesh out a structured persona's freeform fields using Claude.

The deterministic generators produce a coherent *skeleton* (templated bio,
trait lists). This module is the optional bridge to richer, model-written prose:
given a :class:`~persona_factory.models.persona.Persona`, it asks Claude to write
a first-person backstory and (optionally) sample dialogue, then writes them back
onto ``persona.narrative``.

It is intentionally the only part of the package that touches the network. The
``anthropic`` SDK is imported lazily so importing persona-factory never requires
it; a clear :class:`~persona_factory.exceptions.EnrichmentError` is raised if the
``enrichment`` extra is not installed.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from persona_factory.exceptions import EnrichmentError

if TYPE_CHECKING:
    from persona_factory.models.persona import Persona

# Default to Sonnet for a good quality/cost balance on prose generation.
# Documented alternatives: "claude-opus-4-8" (higher quality, higher cost),
# "claude-haiku-4-5" (faster, cheaper).
DEFAULT_MODEL = "claude-sonnet-4-6"

# JSON schema constraining Claude's reply so we can parse it deterministically.
_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "bio": {"type": "string"},
        "backstory": {"type": "string"},
        "sample_dialogue": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["bio", "backstory", "sample_dialogue"],
    "additionalProperties": False,
}


def _load_anthropic() -> Any:
    """Import the anthropic SDK lazily, with a friendly error if it's missing."""
    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - exercised only without extra
        raise EnrichmentError(
            "LLM enrichment requires the 'enrichment' extra: "
            "pip install 'persona-factory[enrichment]'"
        ) from exc
    return anthropic


def _build_prompt(persona: Persona, *, sample_dialogue: bool) -> str:
    """Turn the structured persona into an instruction for the model."""
    facts = json.dumps(persona.to_dict(), ensure_ascii=False, indent=2)
    dialogue_clause = (
        "- `sample_dialogue`: 3 short lines this person might actually say, "
        "in their own voice and communication style.\n"
        if sample_dialogue
        else "- `sample_dialogue`: an empty list.\n"
    )
    return (
        "You are writing character notes for a fictional persona used in an LLM "
        "roleplay / simulation. Below is the structured profile as JSON.\n\n"
        f"{facts}\n\n"
        "Write, grounded in these attributes and consistent with them:\n"
        "- `bio`: a vivid 2-3 sentence third-person biography.\n"
        "- `backstory`: a first-person paragraph (~120 words) in this person's "
        "own voice, reflecting their personality and communication style.\n"
        f"{dialogue_clause}"
        "Stay strictly consistent with the profile. This is a fictional, "
        "synthetic person; do not add real personal data."
    )


def enrich(
    persona: Persona,
    *,
    backstory: bool = True,
    sample_dialogue: bool = False,
    model: str = DEFAULT_MODEL,
    client: Any | None = None,
    max_tokens: int = 1024,
) -> Persona:
    """Enrich ``persona``'s narrative fields with model-written prose, in place.

    Parameters
    ----------
    persona:
        The persona to enrich. Mutated in place (and also returned).
    backstory:
        Whether to (re)write ``narrative.bio`` and ``narrative.backstory``.
    sample_dialogue:
        Whether to also generate ``narrative.sample_dialogue`` lines.
    model:
        Claude model id. Defaults to :data:`DEFAULT_MODEL`
        (``claude-sonnet-4-6``); ``claude-opus-4-8`` and ``claude-haiku-4-5``
        are documented alternatives.
    client:
        An ``anthropic.Anthropic`` instance. If omitted, one is constructed from
        the environment (``ANTHROPIC_API_KEY``).
    max_tokens:
        Output token cap for the generation.

    Returns
    -------
    Persona
        The same persona, with narrative fields populated.

    Raises
    ------
    EnrichmentError
        If the ``enrichment`` extra is not installed or the API call fails.
    """
    if not backstory and not sample_dialogue:
        return persona

    anthropic = _load_anthropic()
    if client is None:
        client = anthropic.Anthropic()

    prompt = _build_prompt(persona, sample_dialogue=sample_dialogue)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            output_config={"format": {"type": "json_schema", "schema": _OUTPUT_SCHEMA}},
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:  # pragma: no cover - network/SDK failures
        raise EnrichmentError(f"LLM enrichment request failed: {exc}") from exc

    text = next(
        (block.text for block in response.content if getattr(block, "type", None) == "text"),
        None,
    )
    if not text:
        raise EnrichmentError("LLM enrichment returned no text content")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise EnrichmentError(f"LLM enrichment returned invalid JSON: {exc}") from exc

    _apply(persona, data, backstory=backstory, sample_dialogue=sample_dialogue)
    return persona


def _apply(
    persona: Persona,
    data: dict[str, Any],
    *,
    backstory: bool,
    sample_dialogue: bool,
) -> None:
    """Write the parsed model output onto the persona's narrative sub-model."""
    from persona_factory.models.persona import Narrative

    if persona.narrative is None:
        persona.narrative = Narrative()
    if backstory:
        if data.get("bio"):
            persona.narrative.bio = data["bio"]
        if data.get("backstory"):
            persona.narrative.backstory = data["backstory"]
    if sample_dialogue and data.get("sample_dialogue"):
        persona.narrative.sample_dialogue = list(data["sample_dialogue"])
