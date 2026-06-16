"""Optional LLM enrichment of generated personas.

This subpackage calls out to an LLM (Anthropic, OpenAI, or OpenRouter) to write
freeform narrative prose. Core persona generation never imports or depends on
it, so generating personas requires no API key or network access.
"""

from __future__ import annotations

from persona_factory.enrichment.llm import enrich

__all__ = ["enrich"]
