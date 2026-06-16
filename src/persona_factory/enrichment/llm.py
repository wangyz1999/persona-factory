"""Flesh out a structured persona's freeform fields using an LLM.

The deterministic generators produce a coherent *skeleton* (templated bio,
trait lists). This module is the optional bridge to richer, model-written prose:
given a :class:`~persona_factory.models.persona.Persona`, it asks an LLM to write
a first-person backstory and (optionally) sample dialogue, then writes them back
onto ``persona.narrative``.

It is intentionally the only part of the package that touches the network. Three
providers are supported, selected via ``provider=``:

* ``"anthropic"`` (default) — Claude, via the ``anthropic`` SDK.
* ``"openai"`` — GPT models, via the ``openai`` SDK.
* ``"openrouter"`` — any OpenRouter-hosted model, via the ``openai`` SDK pointed
  at the OpenRouter base URL.

The provider SDKs are imported lazily so importing persona-factory never forces
a particular client to load.
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

from persona_factory.exceptions import EnrichmentError

if TYPE_CHECKING:
    from persona_factory.models.persona import Persona

# Per-provider default models, chosen for a good quality/cost balance on prose.
# Anthropic alternatives: "claude-opus-4-8" (higher quality), "claude-haiku-4-5".
DEFAULT_MODELS: dict[str, str] = {
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-4o",
    "openrouter": "anthropic/claude-sonnet-4-6",
}
DEFAULT_PROVIDER = "anthropic"

# OpenRouter is OpenAI-API-compatible; the openai SDK just needs its base URL.
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# JSON schema constraining the model's reply so we can parse it deterministically.
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


def _load_sdk(module: str, provider: str) -> Any:
    """Import a provider SDK lazily, with a friendly error if it's missing."""
    try:
        return __import__(module)
    except ImportError as exc:  # pragma: no cover - exercised only without dep
        raise EnrichmentError(
            f"LLM enrichment with provider {provider!r} requires the {module!r} "
            f"package. Install it with: pip install {module}"
        ) from exc


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
        "Reply with ONLY a JSON object with keys `bio`, `backstory`, and "
        "`sample_dialogue`. Stay strictly consistent with the profile. This is a "
        "fictional, synthetic person; do not add real personal data."
    )


def enrich(
    persona: Persona,
    *,
    backstory: bool = True,
    sample_dialogue: bool = False,
    provider: str = DEFAULT_PROVIDER,
    model: str | None = None,
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
    provider:
        Which backend to call: ``"anthropic"`` (default), ``"openai"``, or
        ``"openrouter"``.
    model:
        Model id. Defaults to a sensible per-provider choice
        (see :data:`DEFAULT_MODELS`).
    client:
        A pre-constructed SDK client (``anthropic.Anthropic`` or
        ``openai.OpenAI``). If omitted, one is constructed from the environment
        (``ANTHROPIC_API_KEY`` / ``OPENAI_API_KEY`` / ``OPENROUTER_API_KEY``).
    max_tokens:
        Output token cap for the generation.

    Returns
    -------
    Persona
        The same persona, with narrative fields populated.

    Raises
    ------
    EnrichmentError
        If the provider is unknown, its SDK is not installed, or the API call
        fails.
    """
    if not backstory and not sample_dialogue:
        return persona

    if provider not in DEFAULT_MODELS:
        raise EnrichmentError(
            f"Unknown provider {provider!r}. Choose one of: "
            f"{', '.join(sorted(DEFAULT_MODELS))}."
        )
    if model is None:
        model = DEFAULT_MODELS[provider]

    prompt = _build_prompt(persona, sample_dialogue=sample_dialogue)

    if provider == "anthropic":
        text = _call_anthropic(prompt, model=model, client=client, max_tokens=max_tokens)
    else:
        text = _call_openai(
            prompt, provider=provider, model=model, client=client, max_tokens=max_tokens
        )

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise EnrichmentError(f"LLM enrichment returned invalid JSON: {exc}") from exc

    _apply(persona, data, backstory=backstory, sample_dialogue=sample_dialogue)
    return persona


def _call_anthropic(
    prompt: str, *, model: str, client: Any | None, max_tokens: int
) -> str:
    """Call Claude via the anthropic SDK and return the raw JSON text."""
    if client is None:
        anthropic = _load_sdk("anthropic", "anthropic")
        client = anthropic.Anthropic()

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
    return str(text)


def _call_openai(
    prompt: str, *, provider: str, model: str, client: Any | None, max_tokens: int
) -> str:
    """Call OpenAI/OpenRouter via the openai SDK and return the raw JSON text."""
    if client is None:
        openai = _load_sdk("openai", provider)
        if provider == "openrouter":
            client = openai.OpenAI(
                base_url=_OPENROUTER_BASE_URL,
                api_key=os.environ.get("OPENROUTER_API_KEY"),
            )
        else:
            client = openai.OpenAI()

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:  # pragma: no cover - network/SDK failures
        raise EnrichmentError(f"LLM enrichment request failed: {exc}") from exc

    text = response.choices[0].message.content if response.choices else None
    if not text:
        raise EnrichmentError("LLM enrichment returned no text content")
    return str(text)


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
